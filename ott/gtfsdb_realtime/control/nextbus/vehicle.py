import logging
log = logging.getLogger(__file__)


class Vehicle(object):
    vehicle_id = None
    route_id = None
    direction_id = None
    lat = None
    lon = None
    bearing = None
    age = None

    predictable = False
    speed_kph = None
    dir_tag = None

    def to_str(self):
        print "HI" #self.vehicle_id

    @classmethod
    def xml_to_vehicle(cls, xml):
        """
            <vehicle id="S026" routeTag="193" dirTag="193_1_var0" lat="45.49893" lon="-122.67181" secsSinceReport="12" predictable="true" heading="182" speedKmHr="0" />
        """
        v = Vehicle()

        v.vehicle_id = xml.get('id')
        v.route_id = xml.get('routeTag')
        v.dir_tag = xml.get('dirTag');
        v.direction_id = cls.parse_dir(v.dir_tag)

        v.lat = cls.get_float('lat', xml)
        v.lon = cls.get_float('lon', xml)
        v.bearing = cls.get_float('heading', xml)
        v.speed_kph = cls.get_int('speedKmHr', xml)
        v.age = cls.get_int('secsSinceReport', xml)
        return v

    @classmethod
    def parse_dir(cls, dir_tag):
        return dir_tag

    @classmethod
    def get_int(cls, name, xml):
        return int(xml.get(name))

    @classmethod
    def get_float(cls, name, xml):
        return float(xml.get(name))
