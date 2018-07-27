from pyramid.view import view_config

from ott.gtfsdb_realtime.control.vehicle_queries import VehicleQueries
from ott.utils.parse.url.stop_param_parser import StopParamParser
from ott.utils.parse.url.route_param_parser import RouteParamParser

from ott.utils.svr.pyramid import response_utils
from ott.utils.svr.pyramid.globals import *

import logging
log = logging.getLogger(__file__)


APP_CONFIG=None
def set_app_config(app_cfg):
    """
    called set the singleton AppConfig object
    :see ott.utils.svr.pyramid.app_config.AppConfig :
    """
    global APP_CONFIG
    APP_CONFIG = app_cfg


def do_view_config(cfg):
    cfg.add_route('all_vehicles', '/all_vehicles')
    cfg.add_route('vehicles_via_route', '/vehicles_via_route')
    cfg.add_route('vehicles_via_stop', '/vehicles_via_stop')


@view_config(route_name='all_vehicles', renderer='json', http_cache=CACHE_SHORT)
def all_vehicles(request):
    ret_val = _make_vehicle_response(lambda: VehicleQueries.query_all(APP_CONFIG.db.session))
    return ret_val


@view_config(route_name='vehicles_via_route', renderer='json', http_cache=CACHE_SHORT)
def vehicles_via_route(request):
    p = RouteParamParser.factory(request)
    r = p.get_route_id("-111")
    ret_val = _make_vehicle_response(lambda: VehicleQueries.query_via_route_id(APP_CONFIG.db.session, route_id=r))
    return ret_val


@view_config(route_name='vehicles_via_stop', renderer='json', http_cache=CACHE_SHORT)
def vehicles_via_stop(request):
    p = StopParamParser.factory(request)
    s = p.get_stop_id("-111")
    ret_val = _make_vehicle_response(lambda: VehicleQueries.query_via_stop_id(APP_CONFIG.db.session, stop_id=s))
    return ret_val


def _make_vehicle_response(vehicle_query_call):
    """ util function that wraps various vehicle queries above with boilerplate work to generate the service response """
    #import pdb; pdb.set_trace()
    ret_val = None
    try:
        vehicles_db = vehicle_query_call()
        vehicles_geojson = VehicleQueries.to_geojson(vehicles_db)
        ret_val = response_utils.json_response(vehicles_geojson)
    except Exception as e:
        ret_val = response_utils.sys_error_response()
        log.warn(e)
    finally:
        pass
    return ret_val

