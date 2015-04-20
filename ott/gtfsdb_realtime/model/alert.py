import logging
log = logging.getLogger(__file__)

import datetime
from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime

from ott.gtfsdb_realtime.model.base import Base

class Alert(Base):
    __tablename__ = 'alerts'

    alert_id = Column(String, nullable=False)
    name = Column(String)
    # http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/inheritance.html
    #__mapper_args__ = Base.make_mapper(__tablename__)

    def __init__(self, agency, alert_id):
        self.agency = agency
        self.alert_id = agency

    @classmethod
    def clear_tables(cls, session, agency):
        ''' clear out the positions and vehicles tables
        '''
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
            a = Alert(agency, record)
            #print record
            session.add(a)

            # step 3: update vehicle position

            ret_val = a

        except Exception, err:
            log.exception(err)
            session.rollback()
        finally:
            # step 4:
            try:
                session.commit()
                session.flush()
            except:
                session.rollback()

        return ret_val
