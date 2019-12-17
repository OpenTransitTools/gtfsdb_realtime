import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'ott.utils',
    'argparse',
    'simplejson',
    'geojson',
    'cachetools',
    'requests',

    'gtfsdb',
    'gtfs-realtime-bindings',
    'geoalchemy2',
    'sqlalchemy',
    'zope.sqlalchemy',

    'pyramid',
    'pyramid_tm',
    'pyramid_exclog',
    'waitress',
]

dev_extras = []
extras_require = dict(
    dev=dev_extras
)

oracle_extras = ['cx_oracle>=5.1']
postgresql_extras = ['psycopg2>=2.4.2']

# NOTE: add pyschopg to requires, else pserve is incomplete
requires.append(postgresql_extras)

setup(
    name='ott.gtfsdb_realtime',
    version='0.1.0',
    description='GTFS Real-time Database',
    long_description=README + '\n\n' + CHANGES,
    keywords='GTFS,GTFS-realtime,GTFSRT',
    url='http://opentransittools.com',
    license="Mozilla-derived (http://opentransittools.com)",
    author="Open Transit Tools",
    author_email="info@opentransittools.org",
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla-derived (MPL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
    ),
    dependency_links=[
        'git+https://github.com/OpenTransitTools/utils.git#egg=ott.utils-0.1.0',
        'git+https://github.com/OpenTransitTools/gtfsdb.git#egg=gtfsdb-0.1.7',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require=extras_require,
    entry_points="""\
        [paste.app_factory]
        main = ott.gtfsdb_realtime.pyramid.app:main

        [console_scripts]
        gtfsrt-load = ott.gtfsdb_realtime.loader:main
        gtfsrt-alerts-query = ott.gtfsdb_realtime.control.alert_queries:alerts_command_line
        gtfsrt-vehicles-query = ott.gtfsdb_realtime.control.vehicle_queries:vehicles_command_line
        gtfsrt-vehicles-load = ott.gtfsdb_realtime.loader:load_vehicles
        gtfsrt-nextbus-vehicles = ott.gtfsdb_realtime.control.nextbus.controller:main
    """,

)
