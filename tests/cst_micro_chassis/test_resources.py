from uuid import UUID, uuid4
import datetime

from flask import Flask
from flask import Blueprint
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from cst_micro_chassis import CstMicroChassis
from cst_micro_chassis.resources import ApiResource, ApiPaginatedMixin


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


def test_pagination():
    app = Flask('test-app')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy()
    CstMicroChassis().init_app(app)
    db.init_app(app)

    bp = Blueprint('api', __name__)
    api = Api(bp)

    class Product(db.Model):
        id = db.Column(db.String, unique=True,
                       primary_key=True, default=lambda x: str(uuid4()))
        name = db.Column(db.String)
        created_at = db.Column(db.DateTime)

    class ProductsResource(ApiPaginatedMixin, ApiResource):
        def get(self):
            products = self.get_paginated_query_result(
                Product.query.order_by(Product.created_at.asc())
            )
            serialized = [
                {'name': p.name, 'created': p.created_at.isoformat()}
                for p in products
            ]
            return serialized, 200

    api.add_resource(ProductsResource, '/products')
    app.register_blueprint(bp)
    # adding 107 "products" in db
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            for i in range(107):
                db.session.add(
                    Product(
                        name=f'product No.{i}',
                        created_at=datetime.datetime.utcnow()
                    )
                )
            db.session.commit()

    # fetching the products paginated
    with app.test_client() as c:
        resp = c.get('/products')
        assert resp.status_code == 200
        assert resp.json['meta']['pagination']['prev'] is None
        assert resp.json['meta']['pagination']['next'] == \
               'http://localhost/products?offset=25&limit=25'
        assert len(resp.json['data']) == 25
        for h in resp.headers:
            if h[0] == 'Content-Type':
                assert h[1] == 'application/json'
        crt_page = 1
        while crt_page <= 4:
            next_url = resp.json['meta']['pagination']['next'].split('http://localhost')[-1]
            resp = c.get(next_url)
            import logging
            logging.error(next_url)
            assert resp.status_code == 200
            assert resp.json['meta']['pagination']['prev'] == \
                   f'http://localhost/products?offset={(crt_page-1)*25}&limit=25'
            if crt_page == 4:
                assert resp.json['meta']['pagination']['next'] is None
                assert len(resp.json['data']) == 7
            else:
                assert resp.json['meta']['pagination']['next'] == \
                       f'http://localhost/products?offset={(crt_page + 1) * 25}&limit=25'
                assert len(resp.json['data']) == 25
            crt_page += 1
