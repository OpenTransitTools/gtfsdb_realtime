"""
this response format is one that is modeled after the stop and route responses from OpenTripPlanner
OTP doesn't have vehicle data, but I wanted to model this rt vehicle response on OTP TI, so that
it fits with a style of services from that system
"""
from .vehicle_base import VehicleBase
from .vehicle_base import VehicleListBase

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class Vehicle(VehicleBase):
    def __init__(self, vehicle, index):
        super(Vehicle, self).__init__()
        self.make_vehicle_record(vehicle)

    def make_vehicle_record(self, vehicle):
        """
        :return a vehicle record
        """
        self.rec = {
            "id": "{}-{}-{}".format(vehicle.vehicle_id, vehicle.agency, vehicle.block_id),
            "lon": -000.111,
            "lat": 000.111,
            "heading": float(vehicle.bearing),
            "vehicleId": vehicle.vehicle_id,

            "routeShortName": self.get_route_short_name(vehicle),
            "routeLongName": self.get_route_long_name(vehicle),
            "routeType": vehicle.route_type,
            "routeId": vehicle.route_id,

            "agencyId": vehicle.agency,
            "tripId": vehicle.trip_id,
            "directionId": vehicle.direction_id,
            "serviceId": vehicle.service_id,
            "blockId": vehicle.block_id,
            "shapeId": vehicle.shape_id,
            "stopId": vehicle.stop_id,
            "stopSequence": vehicle.stop_seq,

            "status": vehicle.status,
            "seconds": 0,
            "reportDate": "11.11.2111 11:11 pm",
        }
        self.set_coord(float(vehicle.lat), float(vehicle.lon))
        self.set_time(float(vehicle.timestamp))


class VehicleListResponse(VehicleListBase):

    def __init__(self, vehicles):
        super(VehicleListResponse, self).__init__()
        for i, v in enumerate(vehicles):
            if self.is_valid_vehicle(v):
                v = Vehicle(v, i)
                self.records.append(v)
        self.fix_up()

    @classmethod
    def make_response(cls, vehicles, pretty=True):
        # import time; time.sleep(30);  # test slow connection
        vl = VehicleListResponse(vehicles)
        ret_val = vl.make_json_response(pretty)
        return ret_val