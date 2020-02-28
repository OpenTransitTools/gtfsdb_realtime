import requests
import time

import logging
log = logging.getLogger(__file__)


class Controller(object):
    data = []

    def __init__(self, agency="portland-sc"):
        self.data = self.fetch_vehicles_feed(agency)

    @classmethod
    def fetch_vehicles_feed(cls, agency):
        """
        grab the vehicles feed
        :param agency: portland-sc, etc...
        :return:
        """
        ret_val = None

        # import pdb; pdb.set_trace()
        feed_url = "http://webservices.nextbus.com/service/publicJSONFeed?command=vehicleLocations&t=0&a={}".format(agency)
        log.debug("\nCalling: " + feed_url)
        for n in range(3):
            response = requests.get(feed_url)
            data = response.json()
            if 'vehicle' in data:
                ret_val = data
                break
            time.sleep(1)
        return ret_val

    def vehicle_to_orm(self, session):
        pass

    def vehicle_to_orm(self, session):
        pass


def main():
    v = Controller()
    print(v.data)


if __name__ == '__main__':
    main()

