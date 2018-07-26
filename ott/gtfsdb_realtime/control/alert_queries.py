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
    def query_via_route_id(cls, session, route_id, agency_id=None, stop_id=None, def_val=[]):
        ret_val = def_val
        try:
            log.info("Alerts via route: {}, agency: {}, stop: {}".format(route_id, agency_id, stop_id))
            q = session.query(AlertEntity).filter(AlertEntity.route_id == route_id)
            if agency_id:
                q = q.filter(AlertEntity.agency == agency_id)
            if stop_id:
                q = q.filter(AlertEntity.stop_id == stop_id)
            ret_val = q.all()
        except Exception as e:
            log.warn(e)
        return ret_val

    @classmethod
    def query_via_stop_id(cls, session, stop_id, agency_id=None, def_val=[]):
        ret_val = def_val
        try:
            log.info("Alerts via stop: {0}".format(stop_id))
            q = session.query(AlertEntity).filter(AlertEntity.stop_id == stop_id)
            if agency_id:
                q = q.filter(AlertEntity.agency == agency_id)
            ret_val = q.all()
        except Exception as e:
            log.warn(e)
        return ret_val

    @classmethod
    def query_all(cls, session, agency_id=None, def_val=[]):
        ret_val = def_val
        try:
            q = session.query(AlertEntity)
            if agency_id:
                q = q.filter(AlertEntity.agency == agency_id)
            ret_val = q.all()
        except Exception as e:
            log.warn(e)
        return ret_val

    @classmethod
    def unique_alert_entity_sort(cls, alert_entity_list):
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
        #lambda ret_val : cls.inverse_sort
        return ret_val

    @classmethod
    def print_alert(cls, alert):
        print(alert.description_text)


def get_alerts_cmd():
    """
    cmdline alerts query function
    """
    from ott.utils.parse.cmdline import db_cmdline
    from ott.utils.parse.cmdline import gtfs_cmdline
    from .base import get_session_via_cmdline

    parser = db_cmdline.db_parser('bin/gtfsrt-get-alerts')
    gtfs_cmdline.route_option(parser)
    gtfs_cmdline.stop_option(parser)
    args = parser.parse_args()
    session = get_session_via_cmdline(args)

    ## NOTE: fun little test of casting a Base class in an object to a child
    a = Base()
    a.__class__ = AlertQueries
    a.inverse_sort = False
    print(a.inverse_sort, AlertQueries.inverse_sort)

    #import pdb; pdb.set_trace()
    msg = "VIA"
    if args.route_id or args.stop_id:
        ae = []
        se = []
        if args.route_id:
            msg += " ROUTES"
            ae = a.query_via_route_id(session, args.route_id)
        if args.stop_id:
            msg += " STOPS"
            se = a.query_via_stop_id(session, args.stop_id)
        entities = ae + se
    else:
        msg = "ALL ALERTS"
        entities = a.query_all(session)

    print("\n\n{}:".format(msg))
    for e in entities:
        a.print_alert(e.alert)
