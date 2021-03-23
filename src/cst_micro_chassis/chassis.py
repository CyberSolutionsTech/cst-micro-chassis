import os
from logging.config import dictConfig

from flask import Blueprint, jsonify

from .logging import get_log_config_dict


class CstMicroChassis:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

        self._app = None
        self._db = None

    def init_app(self, app, db=None):
        """
        :param app: Flask app
        :param db: optional - there are services which don't need a db
        :return:
        """
        self._app = app
        self._db = db
        self.setup_logging_config()
        self.register_blueprints()

    def setup_logging_config(self):
        conf_dict = get_log_config_dict(self._app.import_name)
        dictConfig(conf_dict)

    def register_blueprints(self):
        health_check_bp = Blueprint('cst-micro-chassis', self._app.import_name)
        status_endpoint_url = (
                os.environ.get('CST_HEALTH_CHECK_ENDPOINT') or
                self._app.config.get('CST_HEALTH_CHECK_ENDPOINT') or
                'status'
        )
        health_check_bp.add_url_rule(
            f'/{status_endpoint_url.lstrip("/")}',
            view_func=self.status_view,
            endpoint='status'
        )
        self._app.register_blueprint(health_check_bp)

    def status_view(self):
        resp = {
            'name': (
                        os.environ.get('CST_PROJECT_NAME') or
                        self._app.config.get('CST_PROJECT_NAME') or
                        str(self._app.import_name).title()
            ),
            'version': (
                os.environ.get('CST_PROJECT_VERSION') or
                self._app.config.get('CST_PROJECT_VERSION')
                or 'N/A'
            ),
        }
        if self._db:
            conn = self._db.session.connection()
            try:
                last_migration = next(conn.execute(f'SELECT * FROM alembic_version;'))[0]
            except StopIteration:
                last_migration = None
            resp.update({
                'last_migration': last_migration
            })
        return jsonify(resp)
