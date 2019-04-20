"""
this response format is one that is modeled after the stop and route responses from OpenTripPlanner
OTP doesn't have vehicle data, but I wanted to model this rt vehicle response on OTP TI, so that
it fits with a style of services from that system
"""
from .base import Base

import datetime
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)

"""
    "id": "1111-trimet",
    "vehicle": "1111",
    "mode": "BUS",
    "destination": "20  Burnside\/Stark to Gresham TC via Portland City ter",
    "timestamp": 1555555555,

    "lat": 45.5092,
    "lon": -122.773568,
    "heading": 104,
    "lastUpdate": 5,
    "realtimeState": "SCHEDULED",
    "stopId": "1",
    "stopSeq": "1",

    "agencyName": "TriMet",
    "agencyId": "TRIMET",
    "routeShortName": "20",
    "routeId": "20",
    "directionId": "1",
    "tripId": "8983916",
    "blockId": "2074",
    "patternId": "111",
    "serviceId": "111",
    "serviceDay": 1555052400

"""

class Vehicle(object):
    rec = {}

    def __init__(self, vehicle, index):
        self.make_vehicle_record(vehicle, index)

    def make_vehicle_record(self, vehicle, position):
        """
        :return a vehicle record
        """
        self.rec = {
            "id": "{}-{}".format(vehicle.vehicle_id, position.agency),
            "lon": -000.111,
            "lat": 000.111,
            "heading": float(position.bearing),
            "vehicleId": vehicle.vehicle_id,
            "destination": position.headsign,

            "agencyId": position.agency,
            "routeId": position.route_id,
            "tripId": position.trip_id,
            "shapeId": position.shape_id,
            "directionId": position.direction_id,
            "blockId": position.block_id,
            "stopId": position.stop_id,
            "stopSequence": position.stop_seq,

            "status": position.status,
            "seconds": 0,
            "reportDate": "11.11.2111 11:11 pm"
        }
        self.set_coord(float(position.lat), float(position.lon))
        self.set_time(float(position.timestamp))

    def set_coord(self, lat, lon):
        self.rec['lat'] = lat
        self.rec['lon'] = lon

    def set_time(self, time_stamp):
        t = datetime.datetime.fromtimestamp(time_stamp)
        pretty_date_time = t.strftime('%x %I:%M %p').replace(" 0", " ")
        diff = datetime.datetime.now() - t
        self.rec['seconds'] = diff.seconds
        self.rec['reportDate'] = str(pretty_date_time)

    def is_same_block(self, block_id):
        ret_val = False
        if len(self.rec['blockId']) > 0 and self.rec['blockId'] == block_id:
            ret_val = True
        return ret_val

    def merge(self, other_vehicle):
        new_id = self.rec['id'] if self.rec['id'] < other_vehicle.rec['id'] else other_vehicle.rec['id']
        new_vehicle_id = "{}+{}".format(self.rec['vehicleId'], other_vehicle.rec['vehicleId'])

        # step 1: use other record if newer than my record
        if other_vehicle.rec['seconds'] < self.rec['seconds']:
            self.rec = other_vehicle.rec

        # step 2: re-label the vehicle id with a concat of the labels
        self.rec['id'] = new_id
        self.rec['vehicleId'] = new_vehicle_id


class VehicleListResponse(Base):

    def __init__(self, vehicles):
        # import pdb; pdb.set_trace()
        for i, v in enumerate(vehicles):
            v, p = self.get_position(v)
            v = Vehicle(v, p)
            self.records.append(v)
        self.fix_up()

    @classmethod
    def make_response(cls, vehicles, pretty=True):
        vl = VehicleListResponse(vehicles)
        ret_val = vl.make_json_response(pretty)
        return ret_val