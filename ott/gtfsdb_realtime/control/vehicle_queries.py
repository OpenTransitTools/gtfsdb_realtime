from ott.utils.parse.cmdline import db_cmdline
from ott.utils.parse.cmdline import gtfs_cmdline

from .base import get_session_via_cmdline
from .vehicle_geojson import make_response


def query_vehicles(session, routes=None, bbox=None, filter=None):
    """
    query the db and return list of vehicles
    """
    ret_val = []

    from ott.gtfsdb_realtime.model.vehicle import Vehicle
    vehicles = session.query(Vehicle)
    if routes:
        vehicles = vehicles.all()
    elif bbox:
        vehicles = vehicles.all()
    vehicles = vehicles.all()
    for v in vehicles:
        if filter:
            # TODO filers....
            pass
        ret_val.append(v)

    return ret_val


def get_vehicles_cmd():
    """
    bin/gtfsrt-get-vehicles
    """
    parser = db_cmdline.db_parser('bin/gtfsrt-get-vehicles')
    gtfs_cmdline.route_option(parser)
    gtfs_cmdline.stop_option(parser)
    args = parser.parse_args()
    session = get_session_via_cmdline(args)

    # make response objects
    vehicles = query_vehicles(session)
    ret_val = make_response(vehicles)
    return ret_val

