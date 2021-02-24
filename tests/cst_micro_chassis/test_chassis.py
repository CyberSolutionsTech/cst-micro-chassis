
from flask import Flask
from cst_micro_chassis.chassis import CstMicroChassis


def test_flask_extension_generates_healthcheck():
    app = Flask('test-cst-micro-chassis')
    CstMicroChassis().init_app(app)

    with app.test_client() as c:
        app.config['CST_PROJECT_VERSION'] = '0.1.0-4e7205'
        rv = c.get('/status')
        assert rv.status_code == 200
        assert rv.json == {'name': 'Test-Cst-Micro-Chassis', 'version': '0.1.0-4e7205'}
        for h in rv.headers:
            if h[0] == 'Content-Type':
                assert h[1] == 'application/json'
