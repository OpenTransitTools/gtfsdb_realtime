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
        ret_val = None
    except NoResultFound, e:
        log.warn(e)
    except Exception as e:
        log.warn(e)
    finally:
        pass
    return ret_val
