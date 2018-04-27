from ott.gtfsdb_realtime.model.database import Database
from ott.gtfsdb_realtime.model.base import Base

from ott.utils.parse.cmdline import db_cmdline
from ott.utils import string_utils

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


def load_multiple_agency_feeds(session, agency_id, alerts_url=None, trips_url=None, vehicles_url=None):
    """
    This is a main entry for loading one or more GTFS-RT feeds ...
    """
    ret_val = True

    if alerts_url:
        r = load_gtfsrt_feed(session, agency_id, alerts_url)
        if not r:
            ret_val = False

    if trips_url:
        r = load_gtfsrt_feed(session, agency_id, trips_url)
        if not r:
            ret_val = False

    if vehicles_url:
        r = load_gtfsrt_feed(session, agency_id, vehicles_url)
        if not r:
            ret_val = False

    return ret_val


def load_gtfsrt_feed(session, agency_id, feed_url, clear_tables_first=True):
    """
    this is a main entry for loading a single GTFS-RT feed
    the logic here will grab a GTFS-RT feed, and store it in a database
    """
    feed = grab_feed(feed_url)
    feed_type = Base.get_feed_type(feed)
    if feed_type:
        ret_val = store_feed(session, agency_id, feed_type, feed, clear_tables_first)
    else:
        log.warn("not sure what type of data we got back from {}".format(feed_url))
        ret_val = False
    return ret_val


def grab_feed(feed_url):
    """
    :see: https://developers.google.com/transit/gtfs-realtime/examples/
    """
    import urllib
    from google.transit import gtfs_realtime_pb2

    log.info("calling GTFS-RT feed url: {}".format(feed_url))

    # TODO: do we need to close any handlers below?
    feed = gtfs_realtime_pb2.FeedMessage()
    response = urllib.urlopen(feed_url)
    feed.ParseFromString(response.read())
    return feed


def store_feed(session, agency_id, feed_type, feed, clear_tables_first):
    ret_val = False
    try:
        #session.start_trans()
        if clear_tables_first:
            feed_type.clear_tables(session, agency_id)
        feed_type.parse_gtfsrt_feed(session, agency_id, feed)
        ret_val = True
    except Exception as e:
        log.warn(e)
        # session.roll_back()
    finally:
        pass
        # session.end_trans()
    return ret_val


def make_session(url, schema, is_geospatial=False, create_db=False):
    """ wrap Database.make_session() ... might rethink this """
    return Database.make_session(url, schema, is_geospatial, create_db)


def main():
    """ this main() function will call TriMet's GTFS-RT apis by default (as and example of how to load the system) """

    cmdline = db_cmdline.gtfs_rt_parser(api_key_required=True, api_key_msg="Get a TriMet API Key at http://developer.trimet.org/appid/registration")
    args = cmdline.parse_args()

    session = Database.make_session(args.database_url, args.schema, args.is_geospatial, args.create)

    api_key = string_utils.get_val(args.api_key, '<your key here>')
    aurl = string_utils.get_val(args.alerts_url, 'http://trimet.org/transweb/ws/V1/FeedSpecAlerts/includeFuture/true/appId/' + api_key)
    turl = string_utils.get_val(args.trips_url, 'http://trimet.org/transweb/ws/V1/TripUpdate/includeFuture/true/appId/' + api_key)
    vurl = string_utils.get_val(args.vehicles_url, 'http://developer.trimet.org/ws/gtfs/VehiclePositions/includeFuture/true/appId/' + api_key)
    no_errors = load_multiple_agency_feeds(session, args.agency, aurl, turl, vurl)
    if no_errors:
        log.info("Thinking that loading went well...")
    else:
        log.info("Errors Loading???")


if __name__ == '__main__':
    main()

