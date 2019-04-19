import json
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class Base(object):
    records = []

    def make_json_response(self, pretty=True):
        if pretty:
            ret_val = json.dumps(self.records, indent=4, sort_keys=True)
        else:
            ret_val = json.dumps(self.records)
        return ret_val

