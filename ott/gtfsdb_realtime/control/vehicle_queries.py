from ott.utils.parse.cmdline import db_cmdline
from ott.utils.parse.cmdline import gtfs_cmdline

from .base import get_session_via_cmdline
from .base import Base

from ott.gtfsdb_realtime.model.vehicle import Vehicle
from ott.gtfsdb_realtime.model.vehicle_position import VehiclePosition
from ott.gtfsdb_realtime.model.vehicle_geojson import make_response

import datetime
import logging
log = logging.getLogger(__file__)


class VehicleQueries(Base):

    @classmethod
    def query_via_route_id(cls, session, route_id, agency_id=None, limit=None):
        return cls._base_query(session, VehiclePosition, route_id, None, agency_id, limit)

    @classmethod
    def query_via_stop_id(cls, session, stop_id, agency_id=None, limit=None):
        # TODO: really need to look at the trips (and/or routes) that this stop_id serves, and query all eventually hitting that stopt
        return cls._base_query(session, VehiclePosition, None, stop_id, agency_id, limit)

    @classmethod
    def query_all(cls, session, agency_id=None, limit=None):
        return cls._base_query(session, Vehicle, None, None, agency_id, limit)

    @classmethod
    def query_via_route_id(cls, session, route_id, agency_id=None, limit=None):
        return cls._base_query(session, VehiclePosition, route_id, None, agency_id, limit)

    @classmethod
    def unique_sort(cls, vehicle_list):
        """
        de-duplicate and sort alerts from an entity list

        need to cull the list of vehicles for the following reasons...
            a) MAX has 2 vehicles at the same position ... so vehicle_id could be a single id or an array of vehicle ids
            b) the list might be a combo of multiple lists, so we want to dedupe that
            c) junk w/out lat & lon, etc...
            d) sort via (inverse) time maybe?
        """
        stime = datetime.datetime.now()

        ret_val = vehicle_list
        try:
            # step 1: dedupe the list of vehicles
            vehicle_list = list(set(vehicle_list))
            ret_val = vehicle_list

            # step 2: cull any vehicles where position does not have valid coords
            vl = []
            for v in vehicle_list:
                if v.lat and v.lat != 0.0 and v.lon and v.lon != 0.0:
                    vl.append(v)
            vehicle_list = vl
            ret_val = vehicle_list

            # step 3a: sort list based on vehicle ids
            # step Nb: batch any v's that have >=2 matching vehicle ids
            # step Nc: cull down multiple v's with same vehicle_id, saving the last 'good' record

            # step 4a: sort list based on trip ids
            # step Mb: batch any v's that have >=2 matching trip ids
            # step Mc: cull down to single record, either by combining vehicle ids into the list (or throwing out old positions)

            # step 5: sort list based on time
            # ret_val.sort(key=lambda x: x.start, reverse=reverse_sort)
        except Exception as e:
            log.info(e)

        # execution time (debug)
        etime = datetime.datetime.now()
        print(etime - stime)

        return ret_val

    @classmethod
    def to_geojson(cls, vehicles, pretty=False):
        ret_val = make_response(vehicles, pretty)
        return ret_val


def vehicles_command_line():
    """
    command line query of vehicles.
    example:
      bin/gtfsrt-vehicles-cmd -d loc -s trimet -rt "100,75"
    """
    # import pdb; pdb.set_trace()
    parser = db_cmdline.db_parser('bin/gtfsrt-vehicles-cmd')
    gtfs_cmdline.simple_stop_route_parser(parser)
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

    vehicles = VehicleQueries.unique_sort(vehicles)
    ret_val = VehicleQueries.to_geojson(vehicles, pretty=True)
    return ret_val

