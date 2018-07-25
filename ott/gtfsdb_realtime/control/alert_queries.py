

def print_alert(alert):
    print(alert.description_text)


def get_alerts_via_route(session, route_id):
    from ott.gtfsdb_realtime.model.alert_entity import AlertEntity
    entities = AlertEntity.query_via_route_id(session, route_id)
    return entities


def get_alerts_via_stop(session, stop_id):
    print("\n\nVIA STOP " + stop_id)
    from ott.gtfsdb_realtime.model.alert_entity import AlertEntity
    entities = AlertEntity.query_via_stop_id(session, stop_id)
    return entities


def get_all_alerts(session):
    ret_val = []
    from ott.gtfsdb_realtime.model.alert import Alert
    alerts = session.query(Alert).all()
    for a in alerts:
        for e in a.entities:
            ret_val.append(e)
    return ret_val


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

    msg = "VIA"
    if args.route_id or args.stop_id:
        ae = []
        se = []
        if args.route_id:
            msg += " ROUTES"
            ae = get_alerts_via_route(session, args.route_id)
        if args.stop_id:
            msg += " STOPS"
            se = get_alerts_via_stop(session, args.stop_id)
        entities = ae + se
    else:
        msg = "ALL ALERTS"
        entities = get_all_alerts(session)

    print("\n\n", msg, ":")
    for e in entities:
        print_alert(e.alert)
