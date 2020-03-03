import time
import requests

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
                ret_val = data['vehicle']
                break
            time.sleep(1)
        return ret_val

    def to_orm(self, session=None, agency="PSC"):
        """
          {'id': 'S026', 'routeTag': '193',  'lon': '-122.682045', 'lat': '45.520138', 'secsSinceReport': '65', 'dirTag': '193_0_var0', 'heading': '20', 'predictable': 'true', 'speedKmHr': '0' }
        """
        from ott.gtfsdb_realtime.model.vehicle import Vehicle

        orm = []
        for d in self.data:
            v = Vehicle(agency)
            v.id = "{}::{}::{}".format(d.get('id'), agency, d.get('dirTag'))
            v.vehicle_id = id
            v.lon = d.get('lon')
            v.lat = d.get('lat')
            v.bearing = d.get('heading')
            v.speed = d.get('speedKmHr')

            # todo ... need to figure out a lot of junk to fill in below...
            dirTag = d.get('dirTag')
            rdv = []
            if dirTag:
                rdv = dirTag.split("_")
            if len(rdv) < 2:
                rdv = ['x', 'y', 'z']
                log.error("very bad -- NextBus' dirTag not in expected route_dir_pattern format")

            v.route_id = d.get('routeTag')
            v.route_type = "SC"

            v.direction_id = rdv[1]

            v.trip_id = dirTag
            v.block_id = dirTag
            v.service_id = dirTag

            v.route_short_name = rdv[0]
            v.route_long_name = rdv[0]
            v.headsign = rdv[0]

            v.stop_id = ""
            v.stop_seq = 2
            v.status = "X"
            v.timestamp = d.get('secsSinceReport')
            orm.append(v)

            if session:
                session.add(v)

        return orm


def main():
    v = Controller()
    print(v.to_orm())


if __name__ == '__main__':
    main()
