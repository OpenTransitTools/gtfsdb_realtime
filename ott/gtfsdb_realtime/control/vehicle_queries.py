from ott.utils.parse.cmdline import db_cmdline
from ott.utils.parse.cmdline import gtfs_cmdline

from base import get_session_via_cmdline
from base import Base

from ott.gtfsdb_realtime.model.vehicle_geojson import make_response

import logging
log = logging.getLogger(__file__)


class VehicleQueries(Base):

    @classmethod
    def query_via_route_id(cls, session, route_id, agency_id=None, def_val=[]):
        return def_val

    @classmethod
    def query_via_stop_id(cls, session, stop_id, agency_id=None, def_val=[]):
        return def_val

    @classmethod
    def query_all(cls, session, agency_id=None, limit=500, def_val=[]):
        ret_val = def_val

        from ott.gtfsdb_realtime.model.vehicle import Vehicle
        vehicles = session.query(Vehicle).limit(limit).all()
        for v in vehicles:
            ret_val.append(v)
        return ret_val

    @classmethod
    def to_geojson(cls, vehicles, pretty=False):
        ret_val = make_response(vehicles, pretty)
        return ret_val


def get_vehicles_cmd():
    """
    bin/gtfsrt-get-vehicles
    """
    parser = db_cmdline.db_parser('bin/gtfsrt-get-vehicles')
    gtfs_cmdline.simple_stop_route_parser(parser)
    args = parser.parse_args()
    session = get_session_via_cmdline(args)

    # make response objects
    vehicles = VehicleQueries.query_all(session, limit=args.limit)
    ret_val = VehicleQueries.to_geojson(vehicles, pretty=True)

    return ret_val

