import datetime
import geojson

from geoalchemy2 import Geometry
from sqlalchemy import Column, Index, Integer, Numeric, String, Boolean, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.sql import func, and_
from sqlalchemy.orm import deferred, relationship

from ott.gtfsdb_realtime.model.base import Base

class Position(Base):
    ''' holds a history of the coordinates of a vehicle...

        IMPORTANT: datetime.datetime.now() is the datestamp used, which is local to where the server is hosted...
                   this could be problematic for a system that's hosted in a place not in the same timezone as the app.
                   If you ever host this app, and want to host in another locale, you should refactor datetime.datetime.now()
                   so that date is UTC based, etc...
    '''
    __tablename__ = 'positions'

    latest  = Column(Integer, default=1)

    vehicle_fk = Column(Integer, nullable=False)

    lat = Column(Numeric(12,6), nullable=False)
    lon = Column(Numeric(12,6), nullable=False)
    bearing = Column(Numeric(3,3), default=0)

    vehicle_id = Column(String)
    headsign  = Column(String)
    trip_id   = Column(String)
    route_id  = Column(String)
    stop_id   = Column(String)
    stop_seq  = Column(Integer)
    status    = Column(String)
    timestamp = Column(String)

    def set_updated(self):
        self.updated = datetime.datetime.now()
        self.latest = 1

    def set_position(self, lat, lon, bearing=None):
        ''' set the lat / lon of this object, and update the timestamp and 'latest' status (to True)
        '''
        self.set_updated()
        self.lat = lat
        self.lon = lon
        if hasattr(self, 'geom'):
            self.add_geom_to_dict(self.__dict__)

        if bearing:
            self.bearing = bearing

    def set_attributes(self, data):
        #print data, data.current_status
        #import pdb; pdb.set_trace()
        self.vehicle_id = data.vehicle.id
        self.headsign = data.vehicle.label
        self.trip_id = data.trip.trip_id
        self.route_id = data.trip.route_id
        self.stop_id = data.stop_id
        self.stop_seq = data.current_stop_sequence
        self.status = data.VehicleStopStatus.Name(data.current_status)
        self.timestamp = data.timestamp

    @classmethod
    def clear_latest_column(cls, session, agency=''):
        ''' set all latest=True positions to false (for a give car company)
        '''
        session.query(Position).filter(Position.agency == agency).update({'latest': Position.latest + 1})

    @classmethod
    def add_geometry_column(cls, srid=4326):
        cls.geom = Column(Geometry(geometry_type='POINT', srid=srid))

    @classmethod
    def add_geom_to_dict(cls, row, srid=4326):
        row['geom'] = 'SRID={0};POINT({1} {2})'.format(srid, row['lon'], row['lat'])
