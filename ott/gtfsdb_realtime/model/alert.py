import logging
log = logging.getLogger(__file__)

import datetime
from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime

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
    description_text = Column(String(4000))

    def __init__(self, agency, id):
        self.agency = agency
        self.alert_id = id

    @classmethod
    def clear_tables(cls, session, agency):
        ''' clear out the positions and vehicles tables
        '''
        AlertEntity.clear_tables(session, agency)
        session.query(Alert).filter(Alert.agency == agency).delete()

    @classmethod
    def parse_gtfsrt_record(cls, session, agency, record):
        ''' create or update new Alerts and positions
            :return Vehicle object
        '''
        ret_val = None

        try:
            # step 1: query db for vehicle

            # step 2: create or update vehicle
            a = Alert(agency, record.id)
            session.add(a)
            ret_val = a

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
