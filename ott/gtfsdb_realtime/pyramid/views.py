from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import logging
log = logging.getLogger(__file__)

# cache time - affects how long varnish cache will hold a copy of the data
cache_long = 36000  # 10 hours
cache_short = 600   # 10 minutes

system_err_msg = ServerError()
data_not_found = DatabaseNotFound()

# database
DB = None
CONFIG = None


def set_db(db):
    global DB
    DB = db


def set_config(config):
    global CONFIG
    CONFIG = config


def do_view_config(cfg):
    cfg.add_route('all_vehicles', '/all_vehicles')


@view_config(route_name='all_vehicles', renderer='json', http_cache=cache_short)
def all_vehicles(request):
    ret_val = None
    try:
        trip = get_planner().all_vehicles(request)
        ret_val = json_response(trip)
    except NoResultFound, e:
        log.warn(e)
        ret_val = dao_response(data_not_found)
    except Exception as e:
        log.warn(e)
        ret_val = dao_response(system_err_msg)
    finally:
        pass
    return ret_val
