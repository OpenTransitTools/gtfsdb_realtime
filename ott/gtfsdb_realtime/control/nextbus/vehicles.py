import datetime

import logging
log = logging.getLogger(__file__)


class Vehicles(Base):

    def __init__(self, agency, data):
        self.set_attributes(agency, data.vehicle)

    def curl_nextbus_data(self, agency):
        """
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

        :param agency:
        :return:
        """

        self.agency = agency

        self.lat = round(data.position.latitude,  6)
        self.lon = round(data.position.longitude, 6)
        if hasattr(self, 'geom'):
            self.add_geom_to_dict(self.__dict__)

        self.bearing = data.position.bearing
        self.odometer = data.position.odometer
        self.speed = data.position.speed

        self.route_id = data.trip.route_id
        self.route_long_name = data.trip.route_id
        self.route_short_name = data.trip.route_id
        self.route_type = "TRANSIT"
        self.headsign = data.vehicle.label

        self.vehicle_id = data.vehicle.id
        self.trip_id = data.trip.trip_id
        self.stop_id = data.stop_id
        self.stop_seq = data.current_stop_sequence
        self.status = data.VehicleStopStatus.Name(data.current_status)
        self.timestamp = data.timestamp

    def vehicle_to_orm(self, session):
        #import pdb; pdb.set_trace()
