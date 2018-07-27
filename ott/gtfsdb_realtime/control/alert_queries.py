from ott.gtfsdb_realtime.model.alert_entity import AlertEntity

from base import Base

import datetime
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


class AlertQueries(Base):

    # static vals (which can be over-ridden on a class / instance level) to be used by the sort routine
    filter_future = False
    filter_past = True
    inverse_sort = True

    @classmethod
    def query_via_route_id(cls, session, route_id, agency_id=None, limit=None):
        return cls._base_query(session, AlertEntity, route_id, None, agency_id, limit)

    @classmethod
    def query_via_stop_id(cls, session, stop_id, agency_id=None, limit=None):
        return cls._base_query(session, AlertEntity, None, stop_id, agency_id, limit)

    @classmethod
    def query_all(cls, session, agency_id=None, limit=None):
        return cls._base_query(session, AlertEntity, None, None, agency_id, limit)

    @classmethod
    def unique_sort(cls, alert_entity_list):
        """
        de-duplicate and sort alerts from an entity list
        """
        ret_val = []

        # step 1: sort for unique alerts (and also sort past / future, if specified)
        alert_hash = {}
        now = datetime.datetime.now()
        for e in alert_entity_list:
            if cls.filter_past and e.end < now: continue
            if cls.filter_future and e.begin > now: continue
            alert_hash[e.alert_id] = e.alert

        # step 2: sort trips
        ret_val = alert_hash.values()
        # ret_val.sort(key=lambda x: x.start, reverse=reverse_sort)
        return ret_val

    @classmethod
    def print_alert(cls, index="", alert=None):
        print("{}: {}".format(index, alert.description_text))


def get_alerts_cmd():
    """
    cmdline alerts query function
    """
    from ott.utils.parse.cmdline import db_cmdline
    from ott.utils.parse.cmdline import gtfs_cmdline
    from .base import get_session_via_cmdline

    parser = db_cmdline.db_parser('bin/gtfsrt-get-alerts')
    gtfs_cmdline.simple_stop_route_parser(parser)
    args = parser.parse_args()
    session = get_session_via_cmdline(args)

    ## NOTE: fun little test of casting a Base class in an object to a child
    a = Base()
    a.__class__ = AlertQueries
    a.inverse_sort = False
    print(a.inverse_sort, AlertQueries.inverse_sort)

    # import pdb; pdb.set_trace()
    msg = "VIA"
    if args.route_id or args.stop_id:
        ae = []
        se = []
        if args.route_id:
            msg += " ROUTES"
            ae = a.query_via_route_id(session, args.route_id, limit=args.limit)
        if args.stop_id:
            msg += " STOPS"
            se = a.query_via_stop_id(session, args.stop_id, limit=args.limit)
        entities = ae + se
    else:
        msg = "ALL"
        entities = a.query_all(session, limit=args.limit)

    print("\n\n{} ALERTS:".format(msg))
    for i, e in enumerate(entities):
        a.print_alert(i+1, e.alert)
        print("\n")
