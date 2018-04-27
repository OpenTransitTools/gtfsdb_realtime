from sqlalchemy import Column, String, Integer
from sqlalchemy.sql import func, and_

from ott.gtfsdb_realtime.model.base import Base

import logging
log = logging.getLogger(__file__)


class StopTimeUpdate(Base):
    """ https://developers.google.com/transit/gtfs-realtime/examples/
    """
    __tablename__ = 'rt_stop_time_updates'

    trip_id = Column(String, nullable=False)
    stop_id = Column(String, index=True)
    stop_sequence = Column(Integer)

    # Collapsed StopTimeEvent
    arrival_delay = Column(Integer)
    arrival_time = Column(Integer)
    arrival_uncertainty = Column(Integer)

    # Collapsed StopTimeEvent
    departure_delay = Column(Integer)
    departure_time = Column(Integer)
    departure_uncertainty = Column(Integer)

    # TODO: Add domain
    schedule_relationship = Column(String(9))

    @classmethod
    def clear_tables(cls, session, agency, id=None):
        if id:
            session.query(StopTimeUpdate).filter(and_(StopTimeUpdate.agency == agency, StopTimeUpdate.alert_id == id)).delete()
        else:
            session.query(StopTimeUpdate).filter(StopTimeUpdate.agency == agency).delete()
