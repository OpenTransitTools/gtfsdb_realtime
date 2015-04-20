import logging
log = logging.getLogger(__file__)

from sqlalchemy import Column, String
from sqlalchemy.sql import func, and_

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

    @classmethod
    def get_route(cls, session, agency, route_id, short_name=None):
        ret_val = session.query(Route).filter(and_(Route.agency == agency, Route.agency == agency)).first()
        if ret_val is None:
            ret_val = Route(agency, route_id, short_name)
            session.add(ret_val)
            session.commit()
            session.flush()

        return ret_val
