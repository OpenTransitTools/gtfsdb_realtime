import logging
log = logging.getLogger(__file__)

import datetime
from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime
from sqlalchemy.orm import deferred, object_session, relationship

from ott.gtfsdb_realtime.model.base import Base
from ott.gtfsdb_realtime.model.alert_entity import AlertEntity

class Alert(Base):
    __tablename__ = 'alerts'

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

    @classmethod
    def parse_gtfsrt_record(cls, session, agency, record):
        ''' create or update new Alerts and positions
            :return Vehicle object
        '''
        ret_val = None

        try:
            ret_val = Alert(agency, record.id)
            ret_val.set_attributes_via_gtfsrt(record.alert)
            session.add(ret_val)
        except Exception, err:
            log.exception(err)
            session.rollback()
        finally:
            # step 4:
            try:
                AlertEntity.make_entities(session, agency, record.id, record.alert)
                session.commit()
                session.flush()
            except Exception, err:
                log.exception(err)
                session.rollback()

        return ret_val

    @classmethod
    def clear_tables(cls, session, agency):
        ''' clear out the positions and vehicles tables
        '''
        AlertEntity.clear_tables(session, agency)
        session.query(Alert).filter(Alert.agency == agency).delete()

    @classmethod
    def get_route_ids(cls, alert):
        route_ids=[]
        for e in alert.entities:
            if e.route_id:
                route_ids.append(e)
        return route_ids

    @classmethod
    def add_short_names(cls, gtfsdb_session, alert, route_ids=[]):
        ''' add all the route_short_names (from gtfsdb) to the Alert record as a comman separated string
        '''
        if gtfsdb_session:
            short_names = []
            try:
                #import pdb; pdb.set_trace()
                log.debug("query Route table")
                from gtfsdb import Route
                routes = gtfsdb_session.query(Route).filter(Route.route_id.in_(route_ids)).order_by(Route.route_sort_order)
                for r in routes.all():
                    nm = cls.make_pretty_short_name(r)
                    if nm and nm not in short_names:
                        short_names.append(nm)
                alert.route_short_names = ', '.join([str(x) for x in short_names])
            except Exception, e:
                log.exception(e)

    @classmethod
    def make_pretty_short_name(cls, gtfsdb_route):
        ''' override me ... I'm TriMet specific (e.g., MAX, WES)
        '''
        ret_val = None
        if gtfsdb_route.route_short_name and len(gtfsdb_route.route_short_name) > 0:
            ret_val = gtfsdb_route.route_short_name
        elif gtfsdb_route.route_long_name and len(gtfsdb_route.route_long_name) > 0:
            nm = gtfsdb_route.route_long_name
            if "MAX " in nm:
                ret_val = nm.replace(" Line", "")
            elif nm == "WES Commuter Rail":
                ret_val = "WES"
            else:
                ret_val = nm
        return ret_val
