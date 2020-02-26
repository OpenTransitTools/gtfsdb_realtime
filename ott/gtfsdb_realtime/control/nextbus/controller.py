from .vehicle import Vehicle

import requests
import datetime
import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import logging
log = logging.getLogger(__file__)


class Controller(object):
    agency = None
    data = []

    def __init__(self, agency):
        self.agency = agency

    @classmethod
    def grab_feed(cls, agency, parse=True):
        """
        docs:
          https://gist.github.com/grantland/7cf4097dd9cdf0dfed14
          https://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf

        http://webservices.nextbus.com/service/publicJSONFeed?a=portland-sc&t=0&command=vehicleLocations

        Here's the XML from NextBus:
        OLD XML FEED: http://webservices.nextbus.com/s/xmlFeed?command=vehicleLocations&a=portland-sc&t=0
        <body copyright="All data copyright Portland Streetcar 2019.">
            <vehicle id="S026" routeTag="193" dirTag="193_1_var0" lat="45.49893" lon="-122.67181" secsSinceReport="12" predictable="true" heading="182" speedKmHr="0" />
            <vehicle id="S025" routeTag="193" dirTag="193_0_var0" lat="45.49397" lon="-122.67161" secsSinceReport="50" predictable="true" heading="109" speedKmHr="0" />
            <vehicle id="S008" routeTag="194" dirTag="194_0_var1" lat="45.50259" lon="-122.67175" secsSinceReport="3" predictable="true" heading="247" speedKmHr="0" />
            <vehicle id="S005" routeTag="194" dirTag="194_0_var3" lat="45.514515" lon="-122.68504" secsSinceReport="59" predictable="true" heading="25" speedKmHr="0" />
            <vehicle id="S022" routeTag="195" dirTag="195_0_var0" lat="45.513016" lon="-122.6814" secsSinceReport="69" predictable="true" heading="113" speedKmHr="0" />
            <lastTime time="1566411708213" />
        </body>

        How to Match RT Vehicles to TriMet GTFS trips ???:

        http://webservices.nextbus.com/service/publicJSONFeed?a=portland-sc&command=routeList
        {
          "route": [
            {
              "title": "NS North/South",
              "tag": "193"
            },
            {
              "title": "NS Yard",
              "tag": "193Yard"
            },
            {
              "title": "A Loop",
              "tag": "194"
            },
            {
              "title": "B Loop",
              "tag": "195"
            },
            {
              "title": "B NW",
              "tag": "195NW"
            },
            {
              "title": "B Yard",
              "tag": "195Yard"
            }
          ],
          "copyright": "All data copyright Portland Streetcar 2020."
        }

        http://webservices.nextbus.com/service/publicJSONFeed?a=portland-sc&command=routeConfig&r=193
        {
            "route": {
                "stop": [
                    {
                        "title": "SW Lowell & Bond",
                        "stopId": "12881",
                        "tag": "12881",
                        "lon": "-122.67138",
                        "lat": "45.4938999"
                    },
                    {
                        "title": "SW 10th & Clay",
                        "tag": "10765_ar",
                    }
                ],
                "title": "NS North/South",
                "direction": [
                    {
                        "stop": [
                            {   "tag": "12881"  },
                            ........
                            {   "tag": "8989_ar"}
                        ],
                        "useForUI": "true",
                        "tag": "193_0_var0",
                        "title": "NS Line to NW 23rd Ave",
                        "name": "NS Line to NW 23rd Ave"
                    },
                    {
                        "stop": [...]
                        "useForUI": "true",
                        "tag": "193_1_var1",
                        "title": "B Loop to Lloyd via OMSI",
                        "name": "B Loop to Lloyd via OMSI"
                    },
                    {
                        "stop": [...],
                        "useForUI": "true",
                        "tag": "193_1_var0",
                        "title": "NS Line to South Waterfront",
                        "name": "NS Line to South Waterfront"
                    }
                ],
                "path": [ ... ]
            }
        }

        NOTE: Schedule (mucho data) will show you what 'patterns' run on what days, as well as what service keys run etc...
        http://webservices.nextbus.com/service/publicJSONFeed?a=portland-sc&command=schedule&r=193
        {
            "serviceClass": "MoTuWeThFr",
            "title": "NS North/South",
            "tr": [
                {
                    "stop": [
                        {
                            "content": "06:01:00",
                            "tag": "10752",
                            "epochTime": "21660000"
                        },
                        {
                            "content": "06:03:00",
                            "tag": "10753_ar",
                            "epochTime": "21780000"
                        }
                    ],
                    "blockID": "59"
                },
                {
                    "stop": [
                        {
                            "content": "07:16:00",
                            "tag": "10752",
                            "epochTime": "26160000"
                        },
                        {
                            "content": "07:18:00",
                            "tag": "10753_ar",
                            "epochTime": "26280000"
                        }
                    ],
                    "blockID": "56"
                }
            ],
            "direction": "B Loop to Lloyd via OMSI",
            "tag": "193",
            "header": {
                "stop": [
                    {
                        "content": "NW 13th & Lovejoy",
                        "tag": "10752"
                    },
                    {
                        "content": "NW 11th & Johnson",
                        "tag": "10753_ar"
                    }
                ]
            },
            "scheduleClass": "20190901"
        },
        {
            "serviceClass": "MoTuWeThFr",
            "title": "NS North/South",
            "direction": "NS Line to NW 23rd Ave",
            ...
        },
        {
            "serviceClass": "Saturday",
            "title": "NS North/South",
            direction": "NS Line to South Waterfront",
            ...
        },
        {
            "serviceClass": "Sunday",
            "title": "NS North/South",
            "direction": "NS Line to NW 23rd Ave",
            ...
        }

        https://trimet.org/ride/stop_schedule.html?stop_id=10752&sort=destination
        https://trimet.org/ride/stop_schedule.html?stop_id=10753&sort=destination


        other agencies:
         - http://webservices.nextbus.com/service/publicJSONFeed?command=vehicleLocations&a=sf-muni&t=0
         - http://webservices.nextbus.com/service/publicJSONFeed?command=vehicleLocations&a=bat&t=0

        NextBus terms:
           All polling commands, such as for obtaining vehicle locations, should only be run at the most once every 10 seconds
           Interpret this to mean one can call trip updates every 10 secs, and vehicles every 10 secs ...


        :param agency:
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
    v = Controller.grab_feed('portland-sc')
    print(v)


if __name__ == '__main__':
    main()

