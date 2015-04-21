import logging
log = logging.getLogger(__file__)

import datetime
from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime
from sqlalchemy.orm import deferred, object_session, relationship

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

    entities = relationship(
        'AlertEntity',
        primaryjoin='Alert.alert_id == AlertEntity.alert_id',
        foreign_keys='(Alert.alert_id)',
        uselist=True, viewonly=True
    )

    def __init__(self, agency, id):
        self.agency = agency
        self.alert_id = id

    def set_attributes_via_gtfsrt(self, record):
        self.cause = record.DESCRIPTOR.enum_types_by_name['Cause'].values_by_number[record.cause].name
        self.effect = record.DESCRIPTOR.enum_types_by_name['Effect'].values_by_number[record.effect].name

        self.start = record.active_period[0].start
        self.end = record.active_period[0].end
        self.url = self.get_translation(record.url, self.lang)
        self.header_text = self.get_translation(record.header_text, self.lang)
        self.description_text = self.get_translation(record.description_text, self.lang)

    @classmethod
    def parse_gtfsrt_record(cls, session, agency, record):
        ''' create or update new Alerts and positions
            :return Vehicle object
        '''
        ret_val = None

        try:
            ret_val = Alert(agency, record.id)
            ret_val.set_attributes_via_gtfsrt(record.alert)
            session.add(ret_val)
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

    @classmethod
    def clear_tables(cls, session, agency):
        ''' clear out the positions and vehicles tables
        '''
        AlertEntity.clear_tables(session, agency)
        session.query(Alert).filter(Alert.agency == agency).delete()
