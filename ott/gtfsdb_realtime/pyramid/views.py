from pyramid.view import view_config

from ott.gtfsdb_realtime.control.vehicle_queries import VehicleQueries
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


@view_config(route_name='all_vehicles', renderer='json', http_cache=CACHE_SHORT)
def all_vehicles(request):
    ret_val = None
    try:
        vehicles_db = VehicleQueries.query_all(APP_CONFIG.db.session)
        vehicles_geojson = VehicleQueries.to_geojson(vehicles_db)
        ret_val = response_utils.json_response(vehicles_geojson)
    except Exception as e:
        log.warn(e)
    finally:
        pass
    return ret_val
