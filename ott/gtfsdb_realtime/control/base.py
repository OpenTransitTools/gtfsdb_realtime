from ott.utils import db_utils
from ott.gtfsdb_realtime.model.database import Database

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class Base(object):
    def_msg = "abstract method ... not implemented"

    @classmethod
    def query_via_route_id(cls, session, route_id, agency_id=None, limit=None, def_val=[]):
        log.info(cls.def_msg)
        return def_val

    @classmethod
    def query_via_stop_id(cls, session, stop_id, agency_id=None, limit=None, def_val=[]):
        log.info(cls.def_msg)
        return def_val

    @classmethod
    def query_via_coord(cls, session, coord, agency_id=None, limit=None, def_val=[]):
        log.info(cls.def_msg)
        return def_val

    @classmethod
    def query_via_bbox(cls, session, bbox, agency_id=None, limit=None, def_val=[]):
        log.info(cls.def_msg)
        return def_val

    @classmethod
    def query_all(cls, session, agency_id=None, limit=None, def_val=[]):
        log.info(cls.def_msg)
        return def_val

    @classmethod
    def _base_query(cls, session, rt_clazz, route_id, stop_id, agency_id, limit, execute=True, def_val=[]):
        """
        generic query routine for alerts and vehicles
        """
        ret_val = def_val
        try:
            # import pdb; pdb.set_trace()
            log.info("\n query {}: route={}, stop(s)={}, agency={}, limit={}".format(rt_clazz.__tablename__, route_id, agency_id, stop_id, agency_id, limit))
            q = session.query(rt_clazz)
            if route_id:
                if ',' in route_id:
                    l = [x.strip() for x in route_id.split(',')]
                    q = q.filter(rt_clazz.route_id.in_(l))
                else:
                    q = q.filter(rt_clazz.route_id == route_id)
            if stop_id:
                # noinspection PyInterpreter
                if ',' in stop_id:
                    l = [x.strip() for x in stop_id.split(',')]
                    q = q.filter(rt_clazz.stop_id.in_(l))
                else:
                    q = q.filter(rt_clazz.stop_id == stop_id)
            if agency_id:
                q = q.filter(rt_clazz.agency == agency_id)

            # run the query (by default) or return the query for more filtering...
            if execute:
                # note: only apply the limit to a query that will be executed below...
                if limit:
                    q = q.limit(limit)
                ret_val = q.all()
            else:
                ret_val = q
        except Exception as e:
            log.warn(e)

        return ret_val


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
