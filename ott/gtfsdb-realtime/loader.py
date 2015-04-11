from google.transit import gtfs_realtime_pb2
import urllib

feed = gtfs_realtime_pb2.FeedMessage()
response = urllib.urlopen('URL OF YOUR GTFS-REALTIME SOURCE GOES HERE')
feed.ParseFromString(response.read())
for entity in feed.entity:
  if entity.HasField('trip_update'):
    print entity.trip_update
