GTFSDB Realtime
+++++++++++++++

Supported Databases
===================

- PostgreSQL (PostGIS for Geo tables) - preferred
- SQLite - tested
- Oracle - not tested yet
- MySQL  - not tested yet

GTFS REALTIME (General Transit Feed Specification) Database
===========================================================

Python code that will load GTFS-realtime data into a relational database, and SQLAlchemy ORM bindings to the GTFS tables in the gtfsdb.
See https://developers.google.com/transit/gtfs-realtime/


Install and use via the gtfsdb source tree:
==========================================

0. Install Python 2.7, easy_install and buildout on your system...
1. git clone https://github.com/OpenTransitTools/gtfsdb_realtime.git
2. cd gtfsdb_realtime
3. buildout
   NOTE: if you're using postgres, do a 'buildout install prod pg'
4. bin/loader --database_url <db url>  <gtfs file | url>
   examples:
   - bin/loader --database_url sqlite:///gtfsrt.db --url http://developer.trimet.org/ws/gtfs/VehiclePositions/appId/<your app id>
   - bin/loader --database_url sqlite:///gtfsrt.db --url http://developer.trimet.org/ws/gtfs/TripUpdate/appId/<your app id>
   - bin/loader --database_url sqlite:///gtfsrt.db --url http://developer.trimet.org/ws/gtfs/FeedSpecAlerts/includeFuture/true/appId/<your app id>
   - bin/loader --database_url postgresql://postgres@localhost:5432 --schema gtfsdbrt --is_geospatial --url http://developer.trimet.org/ws/gtfs/VehiclePositions/appId/<your app id>

The best way to get gtfsdb_realtime up and running is via the python 'buildout' and 'easy_install' tools.
Highly recommended to first install easy_install (setup tools) and buildout (e.g., easy_install zc.buildout)
before doing anything else.

Postgres users, gtfsdb_realtime requires the psycopg2 database driver. If you are on linux / mac, buildout will install
the necessary dependencies (or re-use whatever you have in your system site-lib). If you are on windows, you most
likely have to find and install a pre-compiled version (see below).


Install Steps (on Windows):
---------------------------
    0. Have a db - docs and examples assume Postgres/PostGIS installed
       http://www.postgresql.org/download/windows
       http://postgis.refractions.net/download/windows/

    1. Python2.7 - http://www.python.org/download/releases/2.7.6/ (python-2.7.6.msi)
       NOTE: see this for setting env variables correctly: http://blog.sadphaeton.com/2009/01/20/python-development-windows-part-1installing-python.html

    2a. Install Setup Tools (easy_install) https://pypi.python.org/pypi/setuptools#windows-8-powershell
    2b. easy_install zc.buildout

    3. Install Psygopg2 (from binary):  http://www.stickpeople.com/projects/python/win-psycopg/

    4. Check out gtfsdb from trunk with Git - see: git clone https://github.com/OpenTransitTools/gtfsdb_realtime.git

    5. cd top level of gtfsdb_realtime tree
    
    6. buildout install prod

    7. bin/loader --database_url <db url>  --url <url to GTFS-realtime data>
