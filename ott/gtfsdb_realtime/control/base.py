from ott.utils import db_utils
from ott.gtfsdb_realtime.model.database import Database


def get_sessiion(args):
    url = db_utils.check_localhost(args.database_url)
    session = Database.make_session(url, args.schema, args.is_geospatial, args.create)
    return session
