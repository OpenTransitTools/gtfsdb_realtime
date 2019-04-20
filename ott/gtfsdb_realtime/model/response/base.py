import json
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)

from operator import itemgetter

class Base(object):
    records = []

    def block_sort(self, vehicles):
        """sort list via block id"""
        sorted(vehicles, key=itemgetter('age'))


    def get_vehicle_recs(self):
        ret_val = []
        for r in self.records:
            ret_val.append(r.rec)
        return ret_val

    def make_json_response(self, pretty=True):
        recs = self.get_vehicle_recs()
        if pretty:
            ret_val = json.dumps(recs, indent=4, sort_keys=True)
        else:
            ret_val = json.dumps(recs)
        return ret_val

    @classmethod
    def get_position(cls, vehicle):
        # note: we might get either Vehicle or Position objects here based on how the query happened
        #       so we first have to get both the position and the vehicle objects
        from ..vehicle_position import VehiclePosition
        if isinstance(vehicle, VehiclePosition):
            position = vehicle
            vehicle = position.vehicle[0]
        else:
            position = vehicle.positions[0]

        return vehicle, position
