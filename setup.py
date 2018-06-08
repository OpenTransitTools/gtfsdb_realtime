import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'ott.utils',
    'gtfsdb',
    'argparse',
    'simplejson',
    'geojson',
    'gtfs-realtime-bindings',
    'geoalchemy2>=0.2.4',
    'sqlalchemy<1.2',  # v1.2 doesn't allow Boolean values of '0' and '1', so this the simple workaround
]


dev_extras = []
oracle_extras = ['cx_oracle>=5.1']
postgresql_extras = ['psycopg2>=2.4.2']

extras_require = dict(
    dev=dev_extras,
    postgresql=postgresql_extras,
)

if sys.version_info[:2] <= (2, 6):
    requires.append('argparse>=1.2.1')
    extras_require['dev'].append('unittest2')

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
        [console_scripts]
        gtfsrt-load = ott.gtfsdb_realtime.loader:main
        gtfsrt-get-alerts = ott.gtfsdb_realtime.control.alert_queries:get_alerts_cmd
        gtfsrt-get-vehicles = ott.gtfsdb_realtime.control.vehicle_queries:get_vehicles_cmd
    """,

)
