import datetime
import json
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class VehicleBase(object):
    rec = None

    def __init__(self):
        self.rec = {}

    def has_same_block(self, other_v):
        ret_val = False
        if len(self.rec['blockId']) > 0 and self.rec['blockId'] == other_v.rec['blockId']:
            ret_val = True
        return ret_val

    def set_coord(self, lat, lon):
        self.rec['lat'] = lat
        self.rec['lon'] = lon

    def has_valid_coords(self):
        ret_val = True
        if self.rec['lat'] is None or self.rec['lat'] == 0.0 or self.rec['lon'] is None or self.rec['lon'] == 0.0:
            ret_val = False
        return ret_val

    def set_time(self, time_stamp):
        t = datetime.datetime.fromtimestamp(time_stamp)
        pretty_date_time = t.strftime('%x %I:%M %p').replace(" 0", " ")
        diff = datetime.datetime.now() - t
        self.rec['seconds'] = diff.seconds
        self.rec['reportDate'] = str(pretty_date_time)

    def merge(self, other_vehicle):
        new_id = self.rec['id'] if self.rec['id'] < other_vehicle.rec['id'] else other_vehicle.rec['id']
        new_vehicle_id = "{}+{}".format(self.rec['vehicleId'], other_vehicle.rec['vehicleId'])

        # step 1: use other record if newer than my record
        if other_vehicle.rec['seconds'] < self.rec['seconds']:
            self.rec = other_vehicle.rec

        # step 2: re-label the vehicle id with a concat of the labels
        self.rec['id'] = new_id
        self.rec['vehicleId'] = new_vehicle_id


class VehicleListBase(object):
    records = None

    def __init__(self):
        self.records = []

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

            # step 2: filter list
            new_list = []
            num_vehicles = len(self.records)
            for i, v in enumerate(self.records):
                #import pdb; pdb.set_trace()

                # step 2a: cull any vehicles where position does not have valid coordinates
                if not v.has_valid_coords():
                    continue

                # step 2b: cull/merge vehicles on same block
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
