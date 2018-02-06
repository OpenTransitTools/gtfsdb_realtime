try:
    import unittest2 as unittest
except ImportError:
    import unittest

from ott.gtfsdb_realtime.model.alert import Alert
from ott.gtfsdb_realtime.model.vehicle import Vehicle
from ott.gtfsdb_realtime.model.database import Database

import logging
log = logging.getLogger(__name__)


class BasicModelTests(object):

    db = None

    url = 'postgresql+psycopg2://geoserve@maps7:5432/ott'
    schema = 'xmas'

    def sess(self):
        if self.db is None:
            self.db = Database(self.url, self.schema)
        return self.db.get_session()


class TestAlerts(unittest.TestCase, BasicModelTests):

    def test_alerts(self):
        alist = self.sess().query(Alert).all()
        self.assertTrue(len(alist) >= 1)

    def test_alert_entity(self):
        alert = self.sess().query(Alert).first()
        self.assertTrue(len(alert.entities) >= 1)


class TestVehicles(unittest.TestCase, BasicModelTests):

    def test_vehicles(self):
        vlist = self.sess().query(Vehicle).all()
        self.assertTrue(len(vlist) >= 1)

    def test_vehicle_positions(self):
        vehicle = self.sess().query(Vehicle).first()
        self.assertTrue(len(vehicle.positions) >= 1)

