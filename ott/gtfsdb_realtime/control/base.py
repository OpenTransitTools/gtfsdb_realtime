from ott.gtfsdb_realtimemodel.database import Database


def get_sessiion(args):
    session = Database.make_session(args.database_url, args.schema, args.is_geospatial, args.create)
    return session
