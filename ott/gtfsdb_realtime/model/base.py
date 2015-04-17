import abc
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime

class _Base(object):

    id = Column(Integer, primary_key=True, nullable=False)
    agency = Column(String, nullable=False)
    created = Column(DateTime, default=datetime.datetime.now())
    updated = Column(DateTime, default=datetime.datetime.now())

    @classmethod
    def get_feed_type(cls, feed):
        '''
        :param data:
        :return: type
        '''
        from .vehicle import Vehicle
        from .alert import Alert
        #from .trip import Trip

        ret_val = None
        for entity in feed.entity:
            if entity.HasField('trip_update'):
                ret_val = Trip
            elif entity.HasField('vehicle'):
                ret_val = Vehicle
            elif entity.HasField('alert'):
                ret_val = Alert
            else:
                continue
            break
        return ret_val

    @classmethod
    def parse_gtfsrt_feed(cls, session, agency, feed):
        '''
        :param session:
        :param agency:
        :param data:
        :return:
        '''
        for record in feed.entity:
            cls.parse_gtfsrt_record(session, agency, record)

    @abc.abstractmethod
    def parse_gtfsrt_record(cls, session, agency, record):
        raise NotImplementedError("Please implement this method")

    @classmethod
    def make_mapper(cls, tablename, column=agency):
        return {
            'polymorphic_on'       : column,
            'polymorphic_identity' : tablename,
            'with_polymorphic'     : '*'
        }

    @classmethod
    def from_dict(cls, attrs):
        clean_dict = cls.make_record(attrs)
        c = cls(**clean_dict)
        return c

    def to_dict(self):
        ''' convert a SQLAlchemy object into a dict that is serializable to JSON
        ''' 
        ret_val = self.__dict__.copy()

        # the __dict__ on a SQLAlchemy object contains hidden crap that we delete from the class dict
        # (not crazy about this hack, but ...) 
        if set(['_sa_instance_state']).issubset(ret_val):
            del ret_val['_sa_instance_state']

        # convert time, date & datetime, etc... objects to iso formats
        for k in ret_val.keys():
            v = ret_val[k] 
            if hasattr(v,"isoformat"):
                ret_val[k] = v.isoformat()

        return ret_val

    @classmethod
    def to_dict_list(cls, list):
        ''' apply to_dict() to all elements in list, and return new / resulting list...
        '''
        ret_val = []
        for l in list:
            if hasattr(l,"to_dict"):
                l = l.to_dict()
            ret_val.append(l)
        return ret_val

    @classmethod
    def bulk_load(cls, engine, records, remove_old=True):
        ''' load a bunch of records at once from a list (first clearing out the table).
            note that the records array has to be dict structures, ala
            http://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.Connection.execute
        '''
        table = cls.__table__
        if remove_old:
            engine.execute(table.delete())
        engine.execute(table.insert(), records)

    @classmethod
    def set_schema(cls, schema):
        # if this is a database table, set the schema
        if hasattr(cls, '__table__'):
            cls.__table__.schema = schema

        # bit of recursion to hit sub classes
        for c in cls.__subclasses__():
            c.set_schema(schema)

    @classmethod
    def set_geometry(cls, is_geospatial=False):
        if is_geospatial:
            if hasattr(cls, 'add_geometry_column'):
                cls.add_geometry_column()

            # bit of recursion to hit sub classes
            for c in cls.__subclasses__():
                c.set_geometry(is_geospatial)



def get_session(self):
        Session = sessionmaker(bind=self.db)
        session = Session()
        return session


Base = declarative_base(cls=_Base)
