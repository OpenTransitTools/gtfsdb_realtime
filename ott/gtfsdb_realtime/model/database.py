from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker

from ott.utils import db_utils
from ott.gtfsdb_realtime.model.base import Base

import logging
log = logging.getLogger(__file__)


class Database(object):
    """
    TODO make this look like gtfsdb's db.py ... things like 'schema', etc...
    """
    db_singleton = None

    def __init__(self, url, schema=None, is_geospatial=False, pool_size=20):
        self.url = url
        self.engine = create_engine(url, poolclass=QueuePool, pool_size=pool_size)
        event.listen(self.engine, 'connect', Database.connection)

        # note ... set these after creating self.engine
        self.schema = schema
        self.is_geospatial = is_geospatial

    def create(self):
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    @classmethod
    def make_session(cls, url, schema, is_geospatial=False, create_db=False, pool_size=20):
        if cls.db_singleton is None:
            cls.db_singleton = Database(url, schema, is_geospatial, pool_size)
            if create_db:
                cls.db_singleton.create()
        session = cls.db_singleton.get_session()
        return session

    @property
    def is_geospatial(self):
        return self._is_geospatial

    @is_geospatial.setter
    def is_geospatial(self, val):
        self._is_geospatial = val
        Base.set_geometry(self._is_geospatial)

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, val):
        # import pdb; pdb.set_trace()
        self._schema = val
        try:
            if self._schema and len(self._schema) > 0:
                from sqlalchemy.schema import CreateSchema
                self.engine.execute(CreateSchema(self._schema))
                Base.set_schema(self._schema)
        except Exception as e:
            log.info("NOTE: couldn't create schema {0} (schema might already exist)\n{1}".format(self._schema, e))

    @classmethod
    def connection(cls, raw_con, connection_record):
        if 'sqlite' in type(raw_con).__module__:
            db_utils.add_math_to_sqllite(raw_con, connection_record)
