import logging
log = logging.getLogger(__file__)

from sqlalchemy import Column, String

from ott.gtfsdb_realtime.model.base import Base

class Route(Base):
    __tablename__ = 'routes'

    route_id = Column(String, nullable=False)
    route_short_name = Column(String)

    def __init__(self, agency, route_id, short_name=None):
        self.agency = agency
        self.route_id = route_id
        self.route_short_name = short_name

    @classmethod
    def clear_tables(cls, session, agency):
        session.query(Route).filter(Route.agency == agency).delete()
