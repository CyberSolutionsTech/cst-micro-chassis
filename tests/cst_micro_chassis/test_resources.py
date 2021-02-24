from flask import Flask
from flask_restful import Api
from cst_micro_chassis import CstMicroChassis
from cst_micro_chassis.resources import ApiResource, ApiPaginatedMixin
from flask import Blueprint
from uuid import UUID


def is_valid_uuid4(string):
    try:
        converted = UUID(string)
        if converted.version == 4:
            return True
    except ValueError:
        pass
    return False


def test_resources_get_201():
    class SimpleResource(ApiResource):
        def get(self):
            msg = 'Hello world'
            return msg, 201

    app = Flask('test-cst-micro-chassis')

    CstMicroChassis().init_app(app)
    bp = Blueprint('api', __name__)
    api = Api(bp)
    api.add_resource(SimpleResource, '/simple', endpoint='simple-endpoint')
    app.register_blueprint(bp)

    with app.test_client() as c:
        resp = c.get('/simple')
        assert resp.status_code == 201
        assert resp.json['data'] == 'Hello world'
        assert is_valid_uuid4(resp.json['meta']['operation_id']) is True
        for h in resp.headers:
            if h[0] == 'Content-Type':
                assert h[1] == 'application/json'


def test_resources_post_400():
    class SimpleResource(ApiResource):
        def post(self, value):
            if value >= 10:
                self.add_error('Value larger than expected 10', path='value')
                return None, 400
            return value ** 2, 200

    app = Flask('test-cst-micro-chassis')

    CstMicroChassis().init_app(app)
    bp = Blueprint('api', __name__)
    api = Api(bp)
    api.add_resource(SimpleResource, '/square/<int:value>', endpoint='square')
    app.register_blueprint(bp)

    with app.test_client() as c:
        # post has an invalid value, no data in response, only errors
        resp = c.post('/square/11')
        assert resp.status_code == 400
        assert 'data' not in resp.json.keys()
        assert resp.json['errors'] == [
            {'message': 'Value larger than expected 10', 'path': 'value'}]

        assert is_valid_uuid4(resp.json['meta']['operation_id']) is True
        for h in resp.headers:
            if h[0] == 'Content-Type':
                assert h[1] == 'application/json'


def test_resources_post_500():
    class SimpleResource(ApiResource):
        def post(self, value):
            division_result = 10 / value
            return division_result, 200

    app = Flask('test-cst-micro-chassis')
    CstMicroChassis().init_app(app)
    bp = Blueprint('api', __name__)
    api = Api(bp)
    api.add_resource(SimpleResource, '/divide/<int:value>', endpoint='divide')
    app.register_blueprint(bp)

    with app.test_client() as c:
        # post has an invalid value, no data in response, only errors
        resp = c.post('/divide/0')
        assert resp.status_code == 500
        for h in resp.headers:
            if h[0] == 'Content-Type':
                assert h[1] == 'application/json'
        assert resp.json == {'message': 'Internal Server Error'}

