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
    route_short_name = Column(String)
    route_type = Column(String)

    stop_id = Column(String)
    trip = Column(String)

    def __init__(self, agency, alert_id):
        self.agency = agency
        self.alert_id = alert_id

    @classmethod
    def clear_tables(cls, session, agency):
        session.query(AlertEntity).filter(AlertEntity.agency == agency).delete()

    @classmethod
    def make_entities(cls, session, agency, record):
        ''' make alert entities, which attach an alert to a route, trip, stop or combination thereof

        :param session:
        :param agency:
        :param record:
        :return:
        '''

        # step 1: remove old entites
        session.query(AlertEntity).filter(and_(AlertEntity.agency == agency, AlertEntity.alert_id == record.id)).delete()

        # step 2: loop thru the entities, and create AlertEntity objects
        for e in record.entities:
            if e:
                a = AlertEntity(agency, record.id)

                session.add(a)

        # step 3: commit objects to db
        session.commit()
        session.flush()
