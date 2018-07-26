from ott.utils import db_utils
from ott.utils import object_utils
from ott.gtfsdb_realtime.model.database import Database

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class Base(object):
    @classmethod
    def query_all(cls, session, agency_id=None, def_val=[]):
        log.info("abstract method")
        return def_val

    @classmethod
    def query_via_route_id(cls, session, route_id, agency_id=None, def_val=[]):
        log.info("abstract method")
        return def_val

    @classmethod
    def query_via_stop_id(cls, session, stop_id, agency_id=None, def_val=[]):
        log.info("abstract method")
        return def_val


def get_session(url, schema=None, is_geospatial=False, create=False):
    session = Database.make_session(url, schema, is_geospatial, create)
    return session


def get_session_via_cmdline(args):
    url = db_utils.check_localhost(args.database_url)
    return get_session(url, args.schema, args.is_geospatial, args.create)


def get_session_via_config(config):
    return make_db_via_config(config).session


def make_db_via_config(config):
    u, s, g = db_utils.db_params_from_config(config)
    db = Database(u, s, g)
    return db
