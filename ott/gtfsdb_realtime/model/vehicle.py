import datetime
from sqlalchemy import Column, Index, Integer, Numeric, String, DateTime
from sqlalchemy.sql import func, and_
from sqlalchemy.orm import deferred, object_session, relationship

from ott.gtfsdb_realtime.model.base import Base
from ott.gtfsdb_realtime.model.position import Position

import logging
log = logging.getLogger(__file__)


class Vehicle(Base):
    __tablename__ = 'rt_vehicles'

    vehicle_id = Column(String, nullable=False)
    license_plate = Column(String)

    positions = relationship(
        'Position',
        primaryjoin='Vehicle.vehicle_id == Position.vehicle_id',
        foreign_keys='(Vehicle.vehicle_id)',
        uselist=True, viewonly=True
    )

    def __init__(self, agency, vehicle_id, license_plate=None):
        self.agency = agency
        self.vehicle_id = vehicle_id
        self.license_plate = license_plate

    @classmethod
    def clear_tables(cls, session, agency):
        """ clear out the positions and vehicles tables
        """
        Position.clear_tables(session, agency)
        session.query(Vehicle).filter(Vehicle.agency == agency).delete()
        session.commit()

    @classmethod
    def parse_gtfsrt_feed(cls, session, agency, feed):
        if feed and feed.entity and len(feed.entity) > 0:
            Position.clear_latest_column(session, agency)
            super(Vehicle, cls).parse_gtfsrt_feed(session, agency, feed)

    @classmethod
    def parse_gtfsrt_record(cls, session, agency, record, timestamp):
        """ create or update new Vehicles and positions
            :return Vehicle object
        """
        ret_val = None
        v = None

        # step 1: query db for vehicle
        try:
            # step 1a: get inner 'vehicle' record
            record = record.vehicle

            # step 1b: see if this is an existing vehicle
            q = session.query(Vehicle).filter(
                and_(
                    Vehicle.vehicle_id == record.vehicle.id,
                    Vehicle.agency == agency,
                )
            )
            v = q.first()
        except Exception, err:
            log.exception(err)

        try:
            # step 2: we didn't find an existing vehicle in the Vehicle table, so add a new one
            if v is None:
                v = Vehicle(agency, record.vehicle.id, record.vehicle.license_plate)
                session.add(v)
                session.commit()
                session.flush()

            # step 2b: set ret_val to our Vehicle (old or new)
            ret_val = v

            # step 3: update the position record if need be
            v.update_position(session, agency, record)
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

    def update_position(self, session, agency, data, time_span=144):
        """ query the db for a position for this vehicle ... if the vehicle appears to be parked in the
            same place as an earlier update, update the 
            NOTE: the position add/update needs to be committed to the db by the caller of this method 
        """

        # step 0: cast some variables
        lat = round(data.position.latitude,  6)
        lon = round(data.position.longitude, 6)

        # step 1: get position object from db ...criteria is to find last position 
        #          update within an hour, and the car hasn't moved lat,lon
        hours_ago = datetime.datetime.now() - datetime.timedelta(hours=time_span)
        p = None
        try:
            q = session.query(Position).filter(
                and_(
                    Position.vehicle_fk == self.id,
                    Position.updated >= hours_ago,
                    Position.lat == lat,
                    Position.lon == lon,
                )
            )
            p = q.first()
        except Exception, err:
            log.exception(err)

        # step 2: we didn't find an existing position in the Position history table, so add a new one
        try:
            if p is None:
                p = Position()
                p.vehicle_fk = self.id
                p.agency = agency
                p.set_attributes(data)
                p.set_position(lat, lon)
                session.add(p)
            else:
                p.set_updated()

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

        return p
