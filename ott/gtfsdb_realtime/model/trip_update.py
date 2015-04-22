import logging
log = logging.getLogger(__file__)

import datetime
from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime
from sqlalchemy.orm import deferred, object_session, relationship

from ott.gtfsdb_realtime.model.base import Base
from ott.gtfsdb_realtime.model.stop_time_update import StopTimeUpdate

class TripUpdate(Base):
    __tablename__ = 'trip_updates'

    trip_id = Column(String, nullable=False, index=True)
    route_id = Column(String, index=True)
    trip_start_time = Column(String)
    trip_start_date = Column(String, index=True)
    schedule_relationship = Column(String)

    # Collapsed VehicleDescriptor
    vehicle_id = Column(String)
    vehicle_label = Column(String)
    vehicle_license_plate = Column(String)

    '''
    entities = relationship(
        'TripUpdate',
        primaryjoin='TripUpdate.trip_id == StopTimeUpdate.trip_id',
        foreign_keys='(TripUpdate.trip_id)',
        uselist=True, viewonly=True
    )
    '''

    def __init__(self, agency, id):
        self.agency = agency
        self.trip_id = id

    def set_attributes_via_gtfsrt(self, record):
        self.route_id = record.trip.route_id
        self.trip_start_time = record.trip.start_time
        self.trip_start_date = record.trip.start_date

        # get the schedule relationship as described in
        # http://code.google.com/apis/protocolbuffers/docs/reference/python/google.protobuf.descriptor.EnumDescriptor-class.html
        self.schedule_relationship = record.trip.ScheduleRelationship.Name(record.trip.schedule_relationship)

        self.vehicle_id = record.vehicle.id
        self.vehicle_label = record.vehicle.label
        self.vehicle_license_plate = record.vehicle.license_plate

    @classmethod
    def parse_gtfsrt_record(cls, session, agency, record, timestamp):
        ''' create a new or update an existing Trip Update record
            :return: TripUpdate object
        '''
        ret_val = None

        try:
            ret_val = TripUpdate(agency, record.trip_update.trip.trip_id)
            ret_val.set_attributes_via_gtfsrt(record.trip_update)
            for stu in record.trip_update.stop_time_update:
                #print stu
                rel = stu.ScheduleRelationship.Name(stu.schedule_relationship)
                s = StopTimeUpdate(
                        agency = agency,
                        trip_id = ret_val.trip_id,
                        schedule_relationship = rel,
                        stop_sequence = stu.stop_sequence,
                        stop_id = stu.stop_id,
                        arrival_delay = stu.arrival.delay,
                        arrival_time = stu.arrival.time,
                        arrival_uncertainty = stu.arrival.uncertainty,
                        departure_delay = stu.departure.delay,
                        departure_time = stu.departure.time,
                        departure_uncertainty = stu.departure.uncertainty,
                )
                session.add(s)
                #ret_val.StopTimeUpdates.append(s)

            session.add(ret_val)
        except Exception, err:
            log.exception(err)
            session.rollback()
        finally:
            try:
                session.commit()
                session.flush()
            except Exception, err:
                log.exception(err)
                session.rollback()

        return ret_val

    @classmethod
    def clear_tables(cls, session, agency):
        ''' clear out the trip_updates table
        '''
        session.query(TripUpdate).filter(TripUpdate.agency == agency).delete()

