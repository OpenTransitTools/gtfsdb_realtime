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
