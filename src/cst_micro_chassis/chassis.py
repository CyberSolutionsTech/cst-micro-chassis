from .logging import setup_logging_config
from flask import Blueprint, jsonify


class CstMicroChassis:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

        self._app_config = None
        self.app_db = None

    def init_app(self, app, db=None):
        """
        :param app: Flask app
        :param db: optional db
        :return:
        """
        self._app_config = app.config
        self.app_db = db
        # setup logging
        setup_logging_config(app)

        # register status endpoint
        health_check_bp = Blueprint('cst-micro-chassis-health-check', app.import_name)
        health_check_bp.add_url_rule('/status', view_func=self.status_view, endpoint='status')
        app.register_blueprint(health_check_bp)

    def status_view(self):
        resp = {
            'name': self._app_config.get('CST_PROJECT_NAME') or 'N/A',
            'version': self._app_config.get('CST_PROJECT_VERSION') or 'N/A',
        }
        if self.app_db:
            conn = self.app_db.session.connection()
            resp.update({
                'last_migration': next(conn.execute('SELECT * FROM alembic_version;'))[0]
            })

        return jsonify(resp)
