from ott.gtfsdb_realtime.model.database import Database
from ott.gtfsdb_realtime.model.base import Base

from ott.utils.parse.cmdline import db_cmdline
from ott.utils import string_utils

import logging
logging.basicConfig()
log = logging.getLogger(__file__)


def parse(session, agency_id, feed_url, clear_first=False):
    """ :see: https://developers.google.com/transit/gtfs-realtime/examples/ """
    from google.transit import gtfs_realtime_pb2
    import urllib

    ret_val = True
    log.warn("agency: {} ... feed url: {}".format(agency_id, feed_url))
    feed = gtfs_realtime_pb2.FeedMessage()
    response = urllib.urlopen(feed_url)
    feed.ParseFromString(response.read())
    feed_type = Base.get_feed_type(feed)
    if feed_type:
        if clear_first:
            feed_type.clear_tables(session, agency_id)
        feed_type.parse_gtfsrt_feed(session, agency_id, feed)
        ret_val = True
    else:
        log.warn("not sure what type of data we've got")
        ret_val = False
    return ret_val


def make_session(url, schema, is_geospatial=False, create_db=False):
    """ wrap Database.make_session() ... might rethink this """
    return Database.make_session(url, schema, is_geospatial, create_db)


def load_agency_data(session, agency_id, alerts_url, trips_url, vehicles_url):
    ret_val = True

    if alerts_url:
        r = parse(session, agency_id, alerts_url)
        if not r:
            ret_val = False

    if trips_url:
        r = parse(session, agency_id, trips_url)
        if not r:
            ret_val = False

    if vehicles_url:
        r = parse(session, agency_id, vehicles_url)
        if not r:
            ret_val = False

    return ret_val


def main():
    cmdline = db_cmdline.gtfs_rt_parser(api_key_required=True, api_key_msg="Get a TriMet API Key at http://developer.trimet.org/appid/registration")
    args = cmdline.parse_args()
    print args

    session = Database.make_session(args.database_url, args.schema, args.is_geospatial, args.create)

    api_key = string_utils.get_val(args.api_key, '<your key here>')
    aurl = string_utils.get_val(args.alerts_url, 'http://trimet.org/transweb/ws/V1/FeedSpecAlerts/includeFuture/true/appId/' + api_key)
    turl = string_utils.get_val(args.trips_url, 'http://trimet.org/transweb/ws/V1/TripUpdate/includeFuture/true/appId/' + api_key)
    vurl = string_utils.get_val(args.vehicles_url, 'http://developer.trimet.org/ws/gtfs/VehiclePositions/includeFuture/true/appId/' + api_key)
    no_errors = load_agency_data(session, args.agency, aurl, turl, vurl)
    if no_errors:
        print "Thinking that loading went well..."
    else:
        print "Errors Loading???"


if __name__ == '__main__':
    main()

