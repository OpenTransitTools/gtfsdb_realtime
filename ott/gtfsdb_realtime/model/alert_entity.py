import logging
log = logging.getLogger(__file__)

from sqlalchemy import Column, String
from sqlalchemy.sql import func, and_

from ott.gtfsdb_realtime.model.base import Base

class AlertEntity(Base):
    ''' https://developers.google.com/transit/gtfs-realtime/examples/alerts
    '''
    __tablename__ = 'alert_entities'

    alert_id = Column(String, nullable=False)

    route_id = Column(String)
    route_type = Column(String)

    stop_id = Column(String)

    # Collapsed TripDescriptor
    trip_id = Column(String)
    trip_route_id = Column(String)
    trip_start_time = Column(String)
    trip_start_date = Column(String, index=True)

    def __init__(self, agency, alert_id):
        self.agency = agency
        self.alert_id = alert_id

    @classmethod
    def clear_tables(cls, session, agency, id=None):
        if id:
            session.query(AlertEntity).filter(and_(AlertEntity.agency == agency, AlertEntity.alert_id == id)).delete()
        else:
            session.query(AlertEntity).filter(AlertEntity.agency == agency).delete()

    @classmethod
    def make_entities(cls, session, agency, alert_id, alert_record):
        ''' make alert entities, which attach an alert to a route, trip, stop or combination thereof
            :see: https://developers.google.com/transit/gtfs-realtime/service-alerts
            :see: https://developers.google.com/transit/gtfs-realtime/examples/alerts

        :param session:
        :param agency:
        :param alert_record:
        :return:
        '''

        # step 1: remove old entites
        cls.clear_tables(session, agency, alert_id)

        # step 2: loop thru the entities, and create AlertEntity objects
        for e in alert_record.informed_entity:
            a = AlertEntity(agency, alert_id)
            a.stop_id = e.stop_id
            a.route_id = e.route_id
            a.route_type = e.route_type
            a.trip_id = e.trip.trip_id
            a.trip_route_id = e.trip.route_id
            a.trip_start_time = e.trip.start_time
            a.trip_start_date = e.trip.start_date
            session.add(a)

        # step 3: commit objects to db
        session.commit()
        session.flush()

    @classmethod
    def add_short_names(cls, gtfsdb_session, alert_orm, route_ids=[]):
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
                alert_orm.route_short_names = ', '.join([str(x) for x in short_names])
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
