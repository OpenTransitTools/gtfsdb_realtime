from pyramid.response import Response
from pyramid.view import view_config

from ott.gtfsdb_realtime.control.vehicle_queries import VehicleQueries

from ott.utils.parse.url.param_parser import ParamParser
from ott.utils.parse.url.geo_param_parser import GeoParamParser

from ott.utils import otp_utils
from ott.utils import json_utils

from ott.utils.svr.pyramid import response_utils
from ott.utils.svr.pyramid import globals

import logging
log = logging.getLogger(__file__)


APP_CONFIG = None
def set_app_config(app_cfg):
    """
    called set the singleton AppConfig object
    :see ott.utils.svr.pyramid.app_config.AppConfig :
    """
    global APP_CONFIG
    APP_CONFIG = app_cfg


"""
Vehicle and companion GTFS (transit) endpoints:

https://modbeta.trimet.org/ws/ti/v0/vehicles/routes/2,4,6
https://modbeta.trimet.org/ws/ti/v0/vehicles/routes/all
https://modbeta.trimet.org/ws/ti/v0/vehicles/stops/2112,2222

https://modbeta.trimet.org/ws/ti/v0/geom/routes/2,4,6
https://modbeta.trimet.org/ws/ti/v0/geom/stops/2,4,6

https://modbeta.trimet.org/ws/ti/v0/geom/patterns/11111,22222,33333
https://modbeta.trimet.org/ws/ti/v0/geom/patterns/stops/11111,22222,33333

"""

def do_view_config(cfg):
    cfg.add_route('all_vehicles', '/vehicles/routes/all')
    cfg.add_route('vehicles_via_route', '/vehicles/routes/{routes}')
    cfg.add_route('vehicles_via_stop', '/vehicles/stops/{stops}')


@view_config(route_name='all_vehicles', renderer='json', http_cache=globals.CACHE_NONE)
def all_vehicles(request):
    ret_val = {}
    with APP_CONFIG.db.managed_session(timeout=10) as session:
        ret_val = _make_vehicle_response(lambda: VehicleQueries.query_all(session))
    return ret_val


@view_config(route_name='vehicles_via_route', renderer='json', http_cache=globals.CACHE_NONE)
def vehicles_via_route(request):
    # import pdb; pdb.set_trace()
    routes = request.matchdict['routes']
    ret_val = _make_vehicle_response(lambda: VehicleQueries.query_via_route_id(APP_CONFIG.db.session, route_id=routes))
    return ret_val


@view_config(route_name='vehicles_via_stop', renderer='json', http_cache=globals.CACHE_NONE)
def vehicles_via_stop(request):
    """
    ret_val = {}
    stop = request.matchdict['stop']
    agency_id, stop_id = otp_utils.breakout_agency_id(stop)
    if agency_id is None:
        agency_id = APP_CONFIG.get_agency(request)
    with APP_CONFIG.db.managed_session(timeout=10) as session:
        s = Stops.stop(session, stop_id, agency_id, detailed=True)
        if s:
            ret_val = s.__dict__
    return ret_val
    """
    p = StopParamParser.factory(request)
    s = p.get_stop_id("-111")
    ret_val = _make_vehicle_response(lambda: VehicleQueries.query_via_stop_id(APP_CONFIG.db.session, stop_id=s))
    return ret_val


def _make_vehicle_response(vehicle_query_call, do_geojson=False):
    """
    util function that wraps various vehicle queries above with boilerplate work to generate the service response
    NOTE: using "lambda: VehicleQueries.x(params...)" above allows me to notate a normal looking function call (complete with params), and
          then pass it here as a parameter the actual call in line of some other code ... very cool (usually hate lamda / anonymous functions, but...)
    """
    # import pdb; pdb.set_trace()
    ret_val = None
    try:
        # step 1: query
        vehicles = vehicle_query_call() # make call to VehcleQueries.query...() within our try/catch
        log.info("number of vehicles: {}".format(len(vehicles)))

        # step 2: convert to either list or geojson response (prep'd for web / python)
        if do_geojson:
            ret_val = VehicleQueries.to_geojson(vehicles, web_response=True)
        else:
            ret_val = VehicleQueries.to_jsonlist(vehicles, web_response=True)
    except Exception as e:
        from ott.utils.svr.pyramid import response_utils
        ret_val = response_utils.sys_error_response()
        log.warning(e)
    finally:
        pass
    return ret_val

