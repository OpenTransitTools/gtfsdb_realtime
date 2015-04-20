import logging
log = logging.getLogger(__file__)

import datetime
from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime

from ott.gtfsdb_realtime.model.base import Base

class Route(Base):
    __tablename__ = 'routes'

    route_id = Column(String, nullable=False)
    route_short_name = Column(String)

