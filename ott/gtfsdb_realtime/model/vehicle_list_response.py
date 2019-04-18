"""
this response format is one that is modeled after the stop and route responses from OpenTripPlanner
OTP doesn't have vehicle data, but I wanted to model this rt vehicle response on OTP TI, so that
it fits with a style of services from that system
"""
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

    def make_vehicle_record(self, v, i):
        """
        :return a vehicle record
        """
        # import pdb; pdb.set_trace()

        # note: we might get either Vehicle or Position objects here based on how the query happened
        #       so we first have to get both the position and the vehicle objects
        from vehicle_position import VehiclePosition
        if isinstance(v, VehiclePosition):
            position = v
            v = position.vehicle[0]
        else:
            position = v.positions[0]

        self.rec = {
            "~unique-id~": str(i),
            "lon": -000.111,
            "lat": 000.111,
            "heading": float(position.bearing),
            "vehicleId": v.vehicle_id,
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
        cls.set_coord(float(position.lat), float(position.lon))
        cls.set_time(position)

    def set_coord(self, lat, lon):
        self.rec.set('lat', lat)
        self.rec.set('lon', lon)

    def set_time(cls, vehicle, position):
        ts = float(position.timestamp)
        t = datetime.datetime.fromtimestamp(ts)
        pretty_date_time = t.strftime('%x %I:%M %p').replace(" 0", " ")

        diff = datetime.datetime.now() - t
        min_sec_diff = divmod(diff.days * 86400 + diff.seconds, 60)

        vehicle["properties"]['minutes'] = min_sec_diff[0]
        vehicle["properties"]['seconds'] = min_sec_diff[1]
        vehicle["properties"]['reportDate'] = str(pretty_date_time)


class VehicleListResponse(object):
    records = []

    def __init__(self, vehicles):
        for i, v in enumerate(vehicles):
            v = Vehcile(v, i)
            self.records.push(v)
