import logging
log = logging.getLogger(__file__)

from sqlalchemy import Column, String
from sqlalchemy.sql import func, and_

from ott.gtfsdb_realtime.model.base import Base

class AlertEntity(Base):
    ''' https://developers.google.com/transit/gtfs-realtime/examples/alerts
    '''
    __tablename__ = 'alert_entities'

    alert_id = Column(String, nullable=False)

    route_id = Column(String)
    route_short_name = Column(String)
    route_type = Column(String)

    stop_id = Column(String)
    trip = Column(String)

    def __init__(self, agency, alert_id):
        self.agency = agency
        self.alert_id = alert_id

    @classmethod
    def clear_tables(cls, session, agency, id=None):
        if id:
            session.query(AlertEntity).filter(and_(AlertEntity.agency == agency, AlertEntity.alert_id == id)).delete()
        else:
            session.query(AlertEntity).filter(AlertEntity.agency == agency).delete()

    @classmethod
    def make_entities(cls, session, agency, alert_id, alert_record):
        ''' make alert entities, which attach an alert to a route, trip, stop or combination thereof

        :param session:
        :param agency:
        :param alert_record:
        :return:
        '''

        # step 1: remove old entites
        cls.clear_tables(session, agency, alert_id)


        # step 2: loop thru the entities, and create AlertEntity objects
        for e in alert_record.informed_entity:
            if e:
                a = AlertEntity(agency, alert_id)
                session.add(a)

        # step 3: commit objects to db
        session.commit()
        session.flush()


    def make_pretty_short_name(r):
        ''' override me ... I'm TriMet specific (e.g., MAX, WES)
        '''
        ret_val = None
        if r.route_short_name and len(r.route_short_name) > 0:
            ret_val = r.route_short_name
        elif r.route_long_name and len(r.route_long_name) > 0:
            nm = r.route_long_name
            if "MAX " in nm:
                ret_val = nm.replace(" Line", "")
            elif nm == "WES Commuter Rail":
                ret_val = "WES"
            else:
                ret_val = nm
        return ret_val


    def add_short_names(opts, alert_orm, route_ids=[]):
        ''' add all the route_short_names (from gtfsdb) to the Alert record as a comman separated string
        '''
        gtfs_db = get_gtfs_db(opts.dsn, opts.schema)
        if gtfs_db:
            short_names = []
            try:
                #import pdb; pdb.set_trace()
                log.debug("query Route table")
                from gtfsdb import Route
                routes = gtfs_db.session.query(Route).filter(Route.route_id.in_(route_ids)).order_by(Route.route_sort_order)
                for r in routes.all():
                    nm = make_pretty_short_name(r)
                    if nm and nm not in short_names:
                        short_names.append(nm)
                alert_orm.route_short_names = ', '.join([str(x) for x in short_names])
            except Exception, e:
                pass