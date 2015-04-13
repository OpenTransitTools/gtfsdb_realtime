import argparse
import logging
log = logging.getLogger(__file__)

from ott.gtfsdb_realtime.model.database import Database

def init_parser():
    parser = argparse.ArgumentParser(
        prog='controller',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--url',
        '-url',
        '-u',
        required='true',
        help="url to gtfs-realtime data"
    )
    parser.add_argument(
        '--database_url',
        '-d',
        required='true',
        help="(geo) database url ala dialect+driver://user:password@host/dbname[?key=value..]"
    )
    parser.add_argument(
        '--schema',
        '-schema',
        '-s',
        help="database schema"
    )
    parser.add_argument(
        '--geo',
        '-geo',
        '-g',
        action="store_true",
        help="add geometry columns"
    )
    parser.add_argument(
        '--create',
        '-create',
        '-c',
        action="store_true",
        help="drop / create database tables for vehicles"
    )
    args = parser.parse_args()
    return args


def parse(args, session):
    from google.transit import gtfs_realtime_pb2
    import urllib

    from ott.gtfsdb_realtime.model.vehicle import Vehicle
    from ott.gtfsdb_realtime.model.alert import Alert

    feed = gtfs_realtime_pb2.FeedMessage()
    url = 'http://trimet.org/transweb/ws/V1/FeedSpecAlerts/appId/3819A6A38C72223198B560DF0/includeFuture/true'
    #url = 'http://trimet.org/transweb/ws/V1/TripUpdate/appId/3819A6A38C72223198B560DF0/includeFuture/true'
    #url = 'http://developer.trimet.org/ws/gtfs/VehiclePositions/appId/3819A6A38C72223198B560DF0'
    agency = "trimet"
    if args.url and len(args.url) > 1:
        url = args.url
    response = urllib.urlopen(url)
    feed.ParseFromString(response.read())
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            data = entity #.trip_update
            #Trip.parse_gtfsrt_data(session, agency, data)
            print data
        elif entity.HasField('vehicle'):
            data = entity.vehicle
            Vehicle.parse_gtfsrt_data(session, agency, data)
        else:
            data = entity
            #print data
            Alert.parse_gtfsrt_data(session, agency, data)

def main():
    #import pdb; pdb.set_trace()
    args = init_parser()
    print args

    db = Database(args.database_url, args.schema, args.geo)
    if args.create:
        db.create()

    session = db.get_session()

    parse(args, session)


if __name__ == '__main__':
    main()
