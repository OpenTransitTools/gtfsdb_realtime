from ott.utils.parse.cmdline import db_cmdline
from ott.utils.parse.cmdline import gtfs_cmdline
from model.database import Database


def get_sessiion(args):
    session = Database.make_session(args.database_url, args.schema, args.is_geospatial, args.create)
    return session

def print_alert(alert):
    print alert.description_text

def get_alerts_via_route(args):
    print "\n\nVIA ROUTE " + args.route_id
    session = get_sessiion(args)
    from model.alert_entity import AlertEntity
    entities = AlertEntity.query_via_route_id(session, args.route_id)
    for e in entities:
        print_alert(e.alert)


def get_alerts_via_stop(args):
    print "\n\nVIA STOP " + args.stop_id
    session = get_sessiion(args)
    from model.alert_entity import AlertEntity
    entities = AlertEntity.query_via_stop_id(session, args.stop_id)
    for e in entities:
        print_alert(e.alert)


def get_all_alerts(args):
    print "\n\nALL ALERTS "
    from model.alert import Alert
    session = get_sessiion(args)
    alerts = session.query(Alert).all()
    for a in alerts:
        for e in a.entities:
            print_alert(e.alert)


def get_alerts():
    parser = db_cmdline.db_parser('bin/gtfsrt-get-alerts')
    gtfs_cmdline.route_option(parser)
    gtfs_cmdline.stop_option(parser)
    args = parser.parse_args()
    if args.route_id:
        get_alerts_via_route(args)
    elif args.stop_id:
        get_alerts_via_stop(args)
    else:
        get_all_alerts(args)
