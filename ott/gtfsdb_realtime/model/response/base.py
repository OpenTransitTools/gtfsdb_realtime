import datetime
import json
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class Base(object):
    records = []

    def has_same_block(self, other_v):
        ret_val = False
        if len(self.rec['blockId']) > 0 and self.rec['blockId'] == other_v.rec['block_id']:
            ret_val = True
        return ret_val

    def fix_up(self):
        """
        de-duplicate and sort alerts from an entity list

        need to cull the list of vehicles for the following reasons...
            a) MAX has 2 vehicles at the same position ... so vehicle_id could be a single id or an array of vehicle ids
            b) the list might be a combo of multiple lists, so we want to dedupe that
            c) junk w/out lat & lon, etc...
            d) sort via (inverse) time maybe?
        """
        stime = datetime.datetime.now()

        try:
            # step 1: sort vehicle records based on block id
            self.records.sort(key=lambda v: v.rec['blockId'], reverse=False)

            # import pdb; pdb.set_trace()

            new_list = []
            num_vehicles = len(self.records)
            for i, v in enumerate(self.records):
                # step 2: cull any vehicles where position does not have valid coords
                if v.rec['lat'] is None or v.rec['lat'] == 0.0 or v.rec['lon'] is None or v.rec['lon'] == 0.0:
                    continue


                # step 3: cull/merge vehicles on same block
                if i+1 < num_vehicles:
                    next_v = self.records[i+1]
                    if next_v and v.has_same_block(next_v):
                        next_v.merge(v)
                        continue

                # step N: add to new list
                new_list.append(v)

                # step 3a: sort list based on vehicle ids
                # step Nb: batch any v's that have >=2 matching vehicle ids
                # step Nc: cull down multiple v's with same vehicle_id, saving the last 'good' record

                # step 4a: sort list based on trip ids
                # step Mb: batch any v's that have >=2 matching trip ids
                # step Mc: cull down to single record, either by combining vehicle ids into the list (or throwing out old positions)

                # step 5: sort list based on time
                # ret_val.sort(key=lambda x: x.start, reverse=reverse_sort)

            # step z: replace old list with fixed up list
            self.records = new_list

        except Exception as e:
            log.info(e)

        # execution time (debug)
        etime = datetime.datetime.now()
        print(etime - stime)

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
