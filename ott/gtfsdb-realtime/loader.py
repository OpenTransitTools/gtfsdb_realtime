from google.transit import gtfs_realtime_pb2
import urllib

feed = gtfs_realtime_pb2.FeedMessage()
url = 'http://trimet.org/transweb/ws/V1/FeedSpecAlerts/appId/3819A6A38C72223198B560DF0/includeFuture/true'
url = 'http://trimet.org/transweb/ws/V1/TripUpdate/appId/3819A6A38C72223198B560DF0/includeFuture/true'
url = 'http://developer.trimet.org/ws/gtfs/VehiclePositions/appId/3819A6A38C72223198B560DF0'
response = urllib.urlopen(url)
feed.ParseFromString(response.read())
for entity in feed.entity:
  print entity
  if entity.HasField('trip_update'):
    print entity.trip_update
