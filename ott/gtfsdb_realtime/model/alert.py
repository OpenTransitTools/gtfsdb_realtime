from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime
from sqlalchemy.orm import deferred, object_session, relationship, backref

from ott.gtfsdb_realtime.model.base import Base
from ott.gtfsdb_realtime.model.alert_entity import AlertEntity

import logging
log = logging.getLogger(__file__)


class Alert(Base):
    __tablename__ = 'rt_alerts'

    alert_id = Column(String, nullable=False)

    start = Column(Integer, index=True)
    end = Column(Integer)

    cause = Column(String)
    effect = Column(String)

    url = Column(String)
    header_text = Column(String)
    description_text = Column(String)

    route_short_names = Column(String)

    entities = relationship(
        'AlertEntity',
        primaryjoin='Alert.alert_id == AlertEntity.alert_id',
        foreign_keys='(Alert.alert_id)',
        backref=backref("alert", lazy="joined", uselist=False),
        uselist=True, viewonly=True
    )

    def __init__(self, agency, id):
        self.agency = agency
        self.alert_id = id

    def set_attributes_via_gtfsrt(self, record):
        self.cause = record.DESCRIPTOR.enum_types_by_name['Cause'].values_by_number[record.cause].name
        self.effect = record.DESCRIPTOR.enum_types_by_name['Effect'].values_by_number[record.effect].name

        self.start = record.active_period[0].start
        self.end = record.active_period[0].end
        self.url = self.get_translation(record.url, self.lang)
        self.header_text = self.get_translation(record.header_text, self.lang)
        self.description_text = self.get_translation(record.description_text, self.lang)

    def get_route_ids(self):
        """ :return list of route ids (could be a single route / single row list) for this alert """
        ret_val = []
        for e in alert.entities:
            if e and e.route_id:
                ret_val.append(e.route_id)
        return ret_val

    def add_short_names(self, gtfsdb_session, sep=', '):
        """
        will add the route_short_names (from gtfsdb) to the Alert record as a comma separated string
        """
        if gtfsdb_session:
            short_names = []
            try:
                route_ids = self.get_route_ids()
                if len(route_ids) > 0:
                    log.debug("query Route table")
                    from gtfsdb import Route
                    routes = gtfsdb_session.query(Route).filter(Route.route_id.in_(route_ids)).order_by(Route.route_sort_order)
                    for r in routes.all():
                        nm = cls.make_pretty_short_name(r)
                        if nm and nm not in short_names:
                            short_names.append(nm)
                    alert.route_short_names = sep.join([str(x) for x in short_names])
            except Exception as e:
                log.exception(e)

    @classmethod
    def parse_gtfsrt_record(cls, session, agency, record, timestamp):
        """
        create or update new Alerts and positions
        """
        ret_val = None

        try:
            ret_val = Alert(agency, record.id)
            ret_val.set_attributes_via_gtfsrt(record.alert)
            session.add(ret_val)
        except Exception as err:
            log.exception(err)
            session.rollback()
        finally:
            try:
                AlertEntity.make_entities(session, agency, record.id, record.alert)
                session.commit()
                ret_val.add_short_names(session)
                session.commit()
                session.flush()
            except Exception as err:
                log.exception(err)
                session.rollback()

        return ret_val

    @classmethod
    def clear_tables(cls, session, agency):
        """
        clear out the positions and vehicles tables
        """
        AlertEntity.clear_tables(session, agency)
        session.query(Alert).filter(Alert.agency == agency).delete()

    @classmethod
    def make_pretty_short_name(cls, gtfsdb_route):
        """
        get either the route short name, or look to convert the route long name into a shorter name...
        NOTE: makes call to an agency_specific... method, which can be overwritten to add customization of long to short name
        """
        ret_val = None
        if gtfsdb_route.route_short_name and len(gtfsdb_route.route_short_name) > 0:
            ret_val = gtfsdb_route.route_short_name
        elif gtfsdb_route.route_long_name and len(gtfsdb_route.route_long_name) > 0:
            nm = gtfsdb_route.route_long_name
            if nm.endswith(" Line"):
                ret_val = nm.replace(" Line", "")
            else:
                ret_val = cls.agency_specific_long_to_short_name(nm)
        return ret_val

    @classmethod
    def agency_specific_long_to_short_name(cls, long_route_name):
        """
        makes for a short name from a route long name
        below is TriMet specific (e.g., WES), so override for different agency
        """
        ret_val = long_route_name
        if nm == "WES Commuter Rail":
            ret_val = "WES"
        return ret_val
