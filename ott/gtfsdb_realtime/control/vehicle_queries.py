from ott.utils.parse.cmdline import db_cmdline
from ott.utils.parse.cmdline import gtfs_cmdline

from .base import Base
from ott.gtfsdb_realtime.model.vehicle import Vehicle

import datetime
import logging
log = logging.getLogger(__file__)


class VehicleQueries(Base):

    @classmethod
    def query_via_route_id(cls, session, route_id, agency_id=None, limit=None):
        # import pdb; pdb.set_trace()
        return cls._base_query(session, Vehicle, route_id, None, agency_id, limit, Vehicle.block_id)

    @classmethod
    def query_via_stop_id(cls, session, stop_id, agency_id=None, limit=None):
        # TODO: really need to look at the trips (and/or routes) that this stop_id serves, and query all eventually hitting that stopt
        return cls._base_query(session, Vehicle, None, stop_id, agency_id, limit, Vehicle.block_id)

    @classmethod
    def query_all(cls, session, agency_id=None, limit=None):
        return cls._base_query(session, Vehicle, None, None, agency_id, limit, Vehicle.block_id)

    @classmethod
    def to_geojson(cls, vehicles, pretty=False):
        from ott.gtfsdb_realtime.model.response.vehicle_geojson import make_response
        ret_val = make_response(vehicles, pretty=pretty)
        return ret_val

    @classmethod
    def to_jsonlist(cls, vehicles, pretty=False):
        from ott.gtfsdb_realtime.model.response.vehicle_list import VehicleListResponse
        ret_val = VehicleListResponse.make_response(vehicles, pretty=pretty)
        log.info("num vehicles: {}, size of ret {}".format(len(vehicles), len(ret_val)))
        return ret_val


def vehicles_command_line():
    """
    command line query of vehicles.
    example:
      bin/gtfsrt-vehicles-cmd -d loc -s trimet -rt "100,75"
    """
    parser = db_cmdline.db_parser('bin/gtfsrt-vehicles-cmd')
    parser = gtfs_cmdline.output_format(parser, detailed=True)
    args = gtfs_cmdline.simple_stop_route_parser(parser)

    # import pdb; pdb.set_trace()
    if args.database_url == 'C' or args.database_url == 'CONFIG':
        from .base import get_session_via_config
        from ott.utils.config_util import ConfigUtil
        config = ConfigUtil.factory(section='gtfs_realtime')
        session = get_session_via_config(config)
    else:
        from .base import get_session_via_cmdline
        session = get_session_via_cmdline(args)

    msg = "VIA"
    vehicles = []
    if args.route_id or args.stop_id:
        ae = []
        se = []
        if args.route_id:
            msg += " ROUTES"
            ae = VehicleQueries.query_via_route_id(session, args.route_id, limit=args.limit)
        if args.stop_id:
            msg += " STOPS"
            se = VehicleQueries.query_via_stop_id(session, args.stop_id, limit=args.limit)
        vehicles = ae + se
    else:
        msg = "ALL"
        vehicles = VehicleQueries.query_all(session, limit=args.limit)

    ret_val = vehicles
    if args.geojson:
        ret_val = VehicleQueries.to_geojson(vehicles, pretty=True)
    elif args.json:
        ret_val = VehicleQueries.to_jsonlist(vehicles, pretty=True)
    return ret_val

