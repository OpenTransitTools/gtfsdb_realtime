from ott.gtfsdb_realtime.model.database import Database


def get_sessiion(args):
    session = Database.make_session(args.database_url, args.schema, args.is_geospatial, args.create)
    return session
