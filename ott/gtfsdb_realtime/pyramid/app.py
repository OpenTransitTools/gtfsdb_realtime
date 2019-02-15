from ott.utils.svr.pyramid.app_config import AppConfig

import logging
log = logging.getLogger(__file__)


def add_cors_headers_response_callback(event):
    MAX_AGE = '1728000'

    """
    add CORS so the requests can work from different (test / development) port
    do this at least for testing ... might not make call in production
    :param event:

    :see config.add_subscriber(add_cors_headers_response_callback, NewRequest):

    :see credit goes to https://stackoverflow.com/users/211490/wichert-akkerman
    :see https://stackoverflow.com/questions/21107057/pyramid-cors-for-ajax-requests
    """
    def cors_headers(request, response):
        response.headers.update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,GET,DELETE,PUT,OPTIONS',
            'Access-Control-Allow-Headers': 'Origin, Content-Type, Accept, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Max-Age': MAX_AGE,
        })
    event.request.add_response_callback(cors_headers)


def main(global_config, **ini_settings):
    """
    this function is the main entry point for pserve / Pyramid
    it returns a Pyramid WSGI application
    see setup.py entry points + config/*.ini [app:main] ala pserve (e.g., bin/pserve config/development.ini)
    """
    app = AppConfig(**ini_settings)

    from pyramid.events import NewRequest
    from zope.sqlalchemy import ZopeTransactionExtension
    from ott.gtfsdb_realtime.model.database import Database
    import views

    u, s, g = app.db_params_from_config()
    db = Database(u, s, g, session_extenstion=ZopeTransactionExtension())
    app.set_db(db)

    app.pyramid.add_subscriber(add_cors_headers_response_callback, NewRequest)

    app.config_include_scan(views)
    return app.make_wsgi_app()

