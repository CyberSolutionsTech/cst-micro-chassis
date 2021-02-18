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
        status_endpoint_url = self._app.config.get('CST_HEALTH_CHECK_ENDPOINT') or 'status'
        health_check_bp.add_url_rule(
            f'/{status_endpoint_url.lstrip("/")}',
            view_func=self.status_view,
            endpoint='status'
        )
        self._app.register_blueprint(health_check_bp)

    def status_view(self):
        resp = {
            'name': self._app.config.get('CST_PROJECT_NAME') or 'N/A',
            'version': self._app.config.get('CST_PROJECT_VERSION') or 'N/A',
        }
        if self._db:
            conn = self._db.session.connection()
            resp.update({
                'last_migration': next(conn.execute('SELECT * FROM alembic_version;'))[0]
            })
        return jsonify(resp)
