from pyramid.config import Configurator

import logging
log = logging.getLogger(__file__)
ECHO = True


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    db = connect(settings)

    # logging config for pserve / wsgi
    if settings and 'logging_config_file' in settings:
        from pyramid.paster import setup_logging
        setup_logging(settings['logging_config_file'])

    import views
    views.set_config(settings)
    views.set_db(db)

    config.include(views.do_view_config)
    config.scan('ott.services.pyramid')

    return config.make_wsgi_app()


def olconnect(settings):
    u = obj.safe_dict_val(settings, 'sqlalchemy.url')
    s = obj.safe_dict_val(settings, 'sqlalchemy.schema')
    g = obj.safe_dict_val(settings, 'sqlalchemy.is_geospatial', False)
    log.info("Database(url={0}, schema={1}, is_geospatial={2})".format(u, s, g))
    return MyGtfsdb(url=u, schema=s, is_geospatial=g)


def pyramid_to_gtfsdb_params(settings):
    global ECHO
    u = obj.safe_dict_val(settings, 'sqlalchemy.url')
    s = obj.safe_dict_val(settings, 'sqlalchemy.schema')
    g = obj.safe_dict_val(settings, 'sqlalchemy.is_geospatial', False)
    ECHO = obj.safe_dict_val(settings, 'sqlalchemy.echo', False)
    return {'url':u, 'schema':s, 'is_geospatial':g}


def connect(settings):
    # import pdb; pdb.set_trace()
    s=pyramid_to_gtfsdb_params(settings)
    log.info("Database({0})".format(s))
    return MyGtfsdb(**s)
