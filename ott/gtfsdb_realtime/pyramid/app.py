from ott.utils.svr.pyramid.app_config import AppConfig

import logging
log = logging.getLogger(__file__)


def main(global_config, **config):
    """
    this function is the main entry point for pserve / Pyramid
    it returns a Pyramid WSGI application
    see setup.py entry points + config/*.ini [app:main] ala pserve (e.g., bin/pserve config/development.ini)
    """
    app = AppConfig(**config)

    from ott.gtfsdb_realtime.control.base import make_db_via_config
    db = make_db_via_config(app.config)
    app.set_db(db)

    import views
    app.config_include_scan(views)
    return app.make_wsgi_app()

