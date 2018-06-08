from ott.utils.parse.cmdline import db_cmdline
from ott.utils.parse.cmdline import gtfs_cmdline
from .base import get_sessiion


def print_alert(alert):
    print alert.description_text


def get_alerts_via_route(args):
    session = get_sessiion(args)
    from model.alert_entity import AlertEntity
    entities = AlertEntity.query_via_route_id(session, args.route_id)
    return entities


def get_alerts_via_stop(args):
    print "\n\nVIA STOP " + args.stop_id
    session = get_sessiion(args)
    from model.alert_entity import AlertEntity
    entities = AlertEntity.query_via_stop_id(session, args.stop_id)
    return entities


def get_all_alerts(args):
    ret_val = []
    from model.alert import Alert
    session = get_sessiion(args)
    alerts = session.query(Alert).all()
    for a in alerts:
        for e in a.entities:
            ret_val.append(e)
    return ret_val


def get_alerts_cmd():
    parser = db_cmdline.db_parser('bin/gtfsrt-get-alerts')
    gtfs_cmdline.route_option(parser)
    gtfs_cmdline.stop_option(parser)
    args = parser.parse_args()

    entities = []
    msg = "VIA"
    if args.route_id or args.stop_id:
        ae = []
        se = []
        if args.route_id:
            msg += " ROUTES"
            ae = get_alerts_via_route(args)
        if args.stop_id:
            msg += " STOPS"
            se = get_alerts_via_stop(args)
        entities = ae + se
    else:
        msg = "ALL ALERTS"
        entities = get_all_alerts(args)

    print "\n\n", msg, ":"
    for e in entities:
        print_alert(e.alert)
