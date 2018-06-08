from ott.utils.parse.cmdline import db_cmdline
from ott.utils.parse.cmdline import gtfs_cmdline

from base import get_sessiion
from vehicle_geojson import make_response


def query_vehicles(args):
    ret_val = []

    """ query the db and return list of vehicles"""
    # todo
    for i in range(10):
        ret_val.append(args)

    return ret_val


def get_vehicles_cmd():
    parser = db_cmdline.db_parser('bin/gtfsrt-get-alerts')
    gtfs_cmdline.route_option(parser)
    gtfs_cmdline.stop_option(parser)
    args = parser.parse_args()

    # make response objects
    vehicles = query_vehicles(args)
    ret_val = make_response(vehicles)
    return ret_val

