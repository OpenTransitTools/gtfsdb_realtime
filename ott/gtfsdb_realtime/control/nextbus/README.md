NOTE: there is possibly a Nextbus gtfs-rt feed out there.  I couldn't find that feed, so I started working on this
loader.  I've put the breaks on the feed due to my colleague Guy saying he could add the Portland SC feed into the
trimet gtfs-rt feed.

This is an early attempt at parsing the Nextbus XML feed, and getting it into the gtfsdb_realtime database.
The code is just at a point of downloading and parsing the data.

TODO:
 - first next task is finding the TRIP_ID for the vehicles (this assumes the vehicles are on schedule ... dangerous assumption)
 - scheduled trip_id could be found via route/trip/date/time 
 - next would be loading this into gtfsdb_realtime
 


