
GTFSDB Realtime
===


Supported Databases
---

- PostgreSQL (PostGIS for Geo tables) - preferred
- SQLite - not tested yet
- Oracle - not tested yet
- MySQL  - not tested yet


GTFS REALTIME (General Transit Feed Specification) Database
--

Python code that will load GTFS-realtime data into a relational database, and SQLAlchemy ORM bindings to the GTFS tables in the gtfsdb.
See https://developers.google.com/transit/gtfs-realtime/


Install and use via the gtfsdb source tree:
---

1. Install Python 2.7, easy_install and buildout on your system...
1. git clone https://github.com/OpenTransitTools/gtfsdb_realtime.git
1. cd gtfsdb_realtime
1. buildout (note: if you're using postgres, do a 'buildout install prod pg')


Run TriMet example:
---
1. get a TriMet api key: http://developer.trimet.org/appid/registration/
1. bin/gtfsdb-rt-loader -a TRIMET -d postgresql+psycopg2://ott@127.0.0.1:5432/ott --api_key <trimet api key> -c ### NOTE: create rt_ tables and populate all services
1. bin/gtfsdb-rt-loader -a TRIMET -d postgresql+psycopg2://ott@127.0.0.1:5432/ott --api_key <trimet api key> -t None -v null ### NOTE: just update the Alerts data (skip trip and vehicle updates)
