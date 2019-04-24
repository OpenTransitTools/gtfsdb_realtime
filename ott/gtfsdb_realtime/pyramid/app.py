from ott.utils.svr.pyramid.app_config import AppConfig

import logging
log = logging.getLogger(__file__)


def main(global_config, **ini_settings):
    """
    this function is the main entry point for pserve / Pyramid
    it returns a Pyramid WSGI application
    see setup.py entry points + config/*.ini [app:main] ala pserve (e.g., bin/pserve config/development.ini)
    """
    app = AppConfig(**ini_settings)


    from zope.sqlalchemy import ZopeTransactionExtension
    from ott.gtfsdb_realtime.model.database import Database
    import views

    u, s, g = app.db_params_from_config()
    db = Database(u, s, g, session_extenstion=ZopeTransactionExtension())
    app.set_db(db)

    # import pdb; pdb.set_trace()
    if ini_settings['pyramid.debug_all']:
        app.add_cors_headers()
    app.config_include_scan(views)
    return app.make_wsgi_app()

