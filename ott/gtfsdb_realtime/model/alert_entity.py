from sqlalchemy import Column, ForeignKey, String, Integer

from ott.gtfsdb_realtime.model.base import Base

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class AlertEntity(Base):
    """
    https://developers.google.com/transit/gtfs-realtime/examples/alerts
    """
    __tablename__ = 'rt_alert_entities'

    alert_id = Column(String, nullable=False)

    route_id = Column(String)
    route_type = Column(String)

    stop_id = Column(String)

    trip_id = Column(String)
    trip_route_id = Column(String)
    trip_start_time = Column(String)
    trip_start_date = Column(String, index=True)

    def __init__(self, agency, alert_id):
        self.agency = agency
        self.alert_id = alert_id

    @classmethod
    def clear_tables(cls, session, agency, alert_id=None):
        q = session.query(AlertEntity).filter(AlertEntity.agency == agency)
        if alert_id:
            q = q.filter(AlertEntity.alert_id == alert_id)
        q.delete()

    @classmethod
    def make_entities(cls, session, agency, alert_id, alert_record, clear_first=True):
        """
        make alert entities, which attach an alert to a route, trip, stop or combination thereof
        :see: https://developers.google.com/transit/gtfs-realtime/service-alerts
        :see: https://developers.google.com/transit/gtfs-realtime/examples/alerts
        """

        # step 1: remove old entites
        if clear_first:
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
    def query_via_route_id(cls, session, route_id, agency_id=None, stop_id=None, def_val=[]):
        """ get array of alerts per route """
        ret_val = def_val
        try:
            log.info("Alerts via route: {}, agency: {}, stop: {}".format(route_id, agency_id, stop_id))
            q = session.query(AlertEntity).filter(AlertEntity.route_id == route_id)
            if agency_id:
                q = q.filter(AlertEntity.agency == agency_id)
            if stop_id:
                q = q.filter(AlertEntity.stop_id == stop_id)
            ret_val = q.all()
        except Exception as e:
            log.warn(e)
        return ret_val

    @classmethod
    def query_via_stop_id(cls, session, stop_id, agency_id=None, def_val=[]):
        ret_val = def_val
        try:
            log.info("Alerts via stop: {0}".format(stop_id))
            q = session.query(AlertEntity).filter(AlertEntity.stop_id == stop_id)
            if agency_id:
                q = q.filter(AlertEntity.agency == agency_id)
            ret_val = q.all()
        except Exception as e:
            log.warn(e)
        return ret_val

    @classmethod
    def unique_alert_entity_sort(cls, alert_entity_list, filter_future=False, filter_past=True, inverse_sort=True):
        """ de-duplicate and sort alerts from an entity list """
        ret_val = []

        # step 1: sort for unique alerts (and also sort past / future, if specified)
        alert_hash = {}
        now = Date.now()
        for e in alert_entity_list:
            if filter_past and e.end < now: continue
            if filter_future and e.begin > now: continue
            alert_hash[e.alert_id] = e.alert

        # step 2: sort trips
        ret_val = alert_hash.values()
        #lambda ret_val : inverse_sort

        return ret_val



