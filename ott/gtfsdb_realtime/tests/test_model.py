try:
    import unittest2 as unittest
except ImportError:
    import unittest

from ott.gtfsdb_realtime.model.alert import Alert
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
        elist = alert.entities
        self.assertTrue(len(elist) >= 1)
