from .vehicle import Vehicle

import urllib
import datetime
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
        docs: https://www.nextbus.com/xmlFeedDocs/NextBusXMLFeed.pdf

        http://webservices.nextbus.com/s/xmlFeed?command=vehicleLocations&a=portland-sc&t=0
        Here's the XML from NextBus:
        <body copyright="All data copyright Portland Streetcar 2019.">
            <vehicle id="S026" routeTag="193" dirTag="193_1_var0" lat="45.49893" lon="-122.67181" secsSinceReport="12" predictable="true" heading="182" speedKmHr="0" />
            <vehicle id="S025" routeTag="193" dirTag="193_0_var0" lat="45.49397" lon="-122.67161" secsSinceReport="50" predictable="true" heading="109" speedKmHr="0" />
            <vehicle id="S008" routeTag="194" dirTag="194_0_var1" lat="45.50259" lon="-122.67175" secsSinceReport="3" predictable="true" heading="247" speedKmHr="0" />
            <vehicle id="S005" routeTag="194" dirTag="194_0_var3" lat="45.514515" lon="-122.68504" secsSinceReport="59" predictable="true" heading="25" speedKmHr="0" />
            <vehicle id="S022" routeTag="195" dirTag="195_0_var0" lat="45.513016" lon="-122.6814" secsSinceReport="69" predictable="true" heading="113" speedKmHr="0" />
            <lastTime time="1566411708213" />
        </body>

        other agencies:
         - http://webservices.nextbus.com/s/xmlFeed?command=vehicleLocations&a=sf-muni&t=0
         -

        NextBus terms:
           All polling commands, such as for obtaining vehicle locations, should only be run at the most once every 10 seconds
           Interpret this to mean one can call trip updates every 10 secs, and vehicles every 10 secs ...


        :param agency:
        :return:
        """
        ret_val = None

        #import pdb; pdb.set_trace()
        feed_url = "http://webservices.nextbus.com/s/xmlFeed?command=vehicleLocations&t=0&a={}".format(agency)
        log.debug("\nCalling: " + feed_url)
        response = urllib.urlopen(feed_url)
        data = response.read()
        if parse:
            if '<' in data and '>' in data:
                tree = ET.fromstring(data)
                children = tree.getchildren()
            else:
                tree = ET.parse(data)
                root = tree.getroot()
                children = root.getchildren()
            ret_val = []
            for xml in children:
                if xml.tag == 'vehicle':
                    v = Vehicle.xml_to_vehicle(xml)
                    ret_val.append(v)
        else:
            ret_val = data
        return ret_val

    def vehicle_to_orm(self, session):
        pass

    def vehicle_to_orm(self, session):
        pass


def main():
    v = Controller.grab_feed('portland-sc')
    print v[0].to_str()

if __name__ == '__main__':
    main()

