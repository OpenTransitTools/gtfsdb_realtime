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

    @classmethod
    def parse_gtfsrt_record(cls, session, agency, record, timestamp):
        ''' create a new or update an existing Trip Update record
            :return: TripUpdate object
        '''
        ret_val = None

        try:
            trip = record.trip_update.trip
            vehicle = record.trip_update.vehicle
            ret_val = TripUpdate(
                agency = agency,
                trip_id = trip.trip_id,
                route_id = trip.route_id,
                trip_start_time = trip.start_time,
                trip_start_date = trip.start_date,
                schedule_relationship = trip.ScheduleRelationship.Name(trip.schedule_relationship),
                vehicle_id = vehicle.id,
                vehicle_label = vehicle.label,
                vehicle_license_plate = vehicle.license_plate,
            )

            for stu in record.trip_update.stop_time_update:
                s = StopTimeUpdate(
                    agency = agency,
                    trip_id = trip.trip_id,
                    schedule_relationship = stu.ScheduleRelationship.Name(stu.schedule_relationship),
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

