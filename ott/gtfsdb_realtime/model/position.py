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

    id = Column(Integer, primary_key=True, nullable=False)
    address = Column(String)
    city = Column(String)
    zipcode = Column(String)
    state = Column(String)
    lat = Column(Numeric(12,9), nullable=False)
    lon = Column(Numeric(12,9), nullable=False)
    created = Column(DateTime, default=datetime.datetime.now())
    updated = Column(DateTime, default=datetime.datetime.now())
    latest  = Column(Boolean,  default=False)

    vehicle_id  = Column(String, nullable=False)
    carshare_co = Column(String, nullable=False)

    '''
    __table_args__ = (
        ForeignKeyConstraint(
              [vehicle_id, carshare_co],
              [Vehicle.id, Vehicle.carshare_company]),
              {}
    )

    vehicle = relation(Vehicle, backref=backref('vehicles', order_by=id, cascade="all, delete-orphan"))
    '''

    def set_position(self, lat, lon, address=None, city=None, state=None, zipcode=None):
        ''' set the lat / lon of this object, and update the timestamp and 'latest' status (to True)
        '''
        self.lat = lat
        self.lon = lon
        if hasattr(self, 'geom'):
            self.add_geom_to_dict(self.__dict__)

        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.updated = datetime.datetime.now()
        self.latest  = True


    @classmethod
    def clear_latest_column(cls, session, car_co=''):
        ''' set all latest=True positions to false (for a give car company)
        '''
        session.query(Position).filter(and_(Position.latest == True, Position.carshare_co == car_co)
                              ).update({"latest":False}, synchronize_session=False)


    @classmethod
    def add_geometry_column(cls, srid=4326):
        cls.geom = Column(Geometry(geometry_type='POINT', srid=srid))

    @classmethod
    def add_geom_to_dict(cls, row, srid=4326):
        row['geom'] = 'SRID={0};POINT({1} {2})'.format(srid, row['lon'], row['lat'])

    @classmethod
    def to_geojson_features(cls, positions):
        ''' loop through list of Position objects and turn them into geojson features
        '''
        ret_val = []
        for i, p in enumerate(positions):
            td = p.updated - p.created
            el = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
            properties = {
                'position_id' : p.id,
                'vehicle_id'  : str(p.vehicle_id),
                'carshare_co' : p.carshare_co,
                'created'     : p.created.isoformat(),
                'updated'     : p.updated.isoformat(),
                'elapsed'     : el
            }
            geo = geojson.Point(coordinates=(p.lon, p.lat))
            f = geojson.Feature(id=i+1, properties=properties, geometry=geo)
            ret_val.append(f)
    
        return ret_val


    @classmethod
    def calc_distance(cls, lon, lat, point):
        '''
            @params: lon, lat, point(lon, lat) ... thing we're comparing to the lon,lat of this object

            @see: http://stackoverflow.com/questions/574691/mysql-great-circle-distance-haversine-formula/574736#574736

            Here's the SQL statement that will find the closest 20 locations that are within a radius of 25 miles to the 
            45.5, -122.5 coordinate. It calculates the distance based on the latitude/longitude of that row and the target 
            latitude/longitude, and then asks for only rows where the distance value is less than 25, orders the whole query
             by distance, and limits it to 20 results. To search by kilometers instead of miles, replace 3959 with 6371.

            Haversine formula
            SELECT( 3959 
                   * acos( 
                        cos( radians(45.5) ) 
                      * cos( radians( lat ) )
                      * cos( radians( lng ) - radians(-122.5) )
                      + sin( radians(45.5) ) * sin( radians( lat ) ) 
                     )
                ) AS distance 

        '''
        haversine = (
                    3959
                    * 
                    func.acos( 
                         func.cos( func.radians(point[1]) )
                         *
                         func.cos( func.radians(lat) )
                         *
                         func.cos( func.radians(lon) - func.radians(point[0]) )
                         +
                         func.sin( func.radians(point[1]) )
                         *
                         func.sin( func.radians(lat) )
                    )
        )
        return haversine
