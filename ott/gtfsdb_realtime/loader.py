from ott.gtfsdb_realtime.model.database import Database
from ott.gtfsdb_realtime.model.base import Base

from ott.utils.parse.cmdline import gtfs_cmdline
from ott.utils import string_utils
from ott.utils import gtfs_utils

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__file__)


def load_agency_feeds(session, agency_id, alerts_url=None, trips_url=None, vehicles_url=None):
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
    download a feed from a url
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
    """
    put a gtfs-rt feed into a database
    """
    ret_val = False

    # step 1: create a savepoint
    session.begin_nested()
    try:
        # step 2: clear content from existing tables
        if clear_tables_first:
            feed_type.clear_tables(session, agency_id)
            # TODO this doesn't seem to be deleting data....
            # TODO: also, do you want to be deleting vehicle position data, if you're recording a history????
            # TODO: we probably need a "clear / don't clear" mechanism on this ... what if we want to append multiple feeds into single table space?

        # step 3: add gtfsrt data to db
        feed_type.parse_gtfsrt_feed(session, agency_id, feed)
        ret_val = True
    except Exception as e:
        # step 4: something bad happened ... roll back to our old savepoint
        session.rollback()
        log.warn(e)
    finally:
        # step 5: commit whatever's in the session
        session.commit()
    return ret_val


def load_feeds_via_config(feed, db_url, is_geospatial=True, create_db=False):
    """
    insert a GTFS feed into configured db
    """
    ret_val = True

    # step 1: agency and schema
    agency_id = feed.get('agency_id')
    schema = feed.get('schema', agency_id.lower())

    # step 2: get urls to this feed's
    trips_url = gtfs_utils.get_realtime_trips_url(feed)
    alerts_url = gtfs_utils.get_realtime_alerts_url(feed)
    vehicles_url = gtfs_utils.get_realtime_vehicles_url(feed)

    # step 3: load them there gtfs-rt feeds
    try:
        log.info("loading gtfsdb_realtime db {} {}".format(db_url, schema))
        session = Database.make_session(db_url, schema, is_geospatial, create_db)
        ret_val = load_agency_feeds(session, agency_id, trips_url, alerts_url, vehicles_url)
    except Exception as e:
        log.error("DATABASE ERROR : {}".format(e))
        ret_val = False

    return ret_val


def load_feeds_via_cmdline():
    """ this main() function will call TriMet's GTFS-RT apis by default (as and example of how to load the system) """
    # import pdb; pdb.set_trace()

    cmdline = gtfs_cmdline.gtfs_rt_parser(api_key_required=True, api_key_msg="Get a TriMet API Key at http://developer.trimet.org/appid/registration")
    args = cmdline.parse_args()

    schema = string_utils.get_val(args.schema, args.agency.lower())
    session = Database.make_session(args.database_url, schema, args.is_geospatial, args.create)

    api_key = string_utils.get_val(args.api_key, '<your key here>')
    aurl = string_utils.get_val(args.alerts_url, 'http://developer.trimet.org/ws/V1/FeedSpecAlerts/includeFuture/true/appId/' + api_key)
    turl = string_utils.get_val(args.trips_url, 'http://developer.trimet.org/ws/V1/TripUpdate/appId/' + api_key)
    vurl = string_utils.get_val(args.vehicles_url, 'http://developer.trimet.org/ws/gtfs/VehiclePositions/appId/' + api_key)
    no_errors = load_agency_feeds(session, args.agency, aurl, turl, vurl)
    if no_errors:
        log.info("Thinking that loading went well...")
    else:
        log.info("Errors Loading???")


def main():
    load_feeds_via_cmdline()

if __name__ == '__main__':
    main()

