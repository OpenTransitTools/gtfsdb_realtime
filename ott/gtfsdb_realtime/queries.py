from ott.utils.parse.cmdline import db_cmdline
from ott.utils.parse.cmdline import gtfs_cmdline
from model.database import Database


def get_alerts():
    from model.alert_entity import AlertEntity
    parser = db_cmdline.db_parser('bin/gtfsrt-get-alerts')
    gtfs_cmdline.route_option(parser)
    args = parser.parse_args()

    session = Database.make_session(args.database_url, args.schema, args.is_geospatial, args.create)
    alerts = AlertEntity.query_via_route_id(session, args.route_id)
    print alerts


def main():
    get_alerts()


if __name__ == '__main__':
    main()