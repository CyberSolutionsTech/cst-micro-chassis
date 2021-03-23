## Cst-Micro-Chassis

---

Cst-Micro-Chassis is a [chassis framework](https://microservices.io/patterns/microservice-chassis.html) for creating REST-ful APIs based on Flask and Flask-Restful. 

The main topics covered are: 

 1. A uniform API response format
 2. API pagination
 3. Logging
 4. Health check

---
#### Installation
```shell
pip install cst-micro-chassis
```

---
#### Usage


Import and initialize with a flask app (as you would usually do with any other flask extension)

```python
from flask import Flask
from cst_micro_chassis import CstMicroChassis

app = Flask('my-first-cst-app')
CstMicroChassis.init_app(app)
```

doing this will initialize the CstMicroChassis core class, setting up the default logging format across your app together with a ready-to-use health check endpoint.

The default url route for the health check endpoint is `/status`, so doing a `curl localhost/status ` should return 
```json
{
  "name": "My-First-Cst-App",
  "version": "N/A"
}
```
with `Content-Type: application/json`

Setting a custom name and version for the application can be done by setting the `CST_PROJECT_NAME` and `CST_PROJECT_VERSION`, either as environment variables or flask config variables. 

You may also want to set a custom url route instead of the standard `/status` ; this can be done setting `CST_HEALTH_CHECK_ENDPOINT=/my-custom-status` environment or flask variable.

If the flask application also uses Flask-SQLAlchemy + migrate and alembic, you can also provide the Flask-SQLAlchemy instance as an optional argument to the chassis init_app method like this

```python
# import Flask, SQLAlchemy, Migrate, CstMicroChassis 
app = Flask('my-first-cst-app-with-db')
db = SQLAlchemy()
migrate = Migrate()
db.init_app()
migrate.init_app(app, db)

CstMicroChassis.init_app(app, db)

```
doing now a `curl localhost/status ` should return also the latest migration from the `alembic_version` database table:

```json
{
  "name": "My-First-Cst-App-With-DB",
  "version": "N/A",
  "last_migration": "ef123ae24f13"
}
```

##### LOGGING

As mentioned above, a custom logging configuration was set for your flask application, so when using the logging module: 
```python
import logging 
logger = logging.getLogger(__name__)
logger.warning('Hello CST')
```

the stdout output will be:

    2021-02-22 16:42:54,923 [WARNING][No operation_id] myapp: Hello CST
matching the format  

    <datetime> [<log_level>][<operation_id>] <module_name>: <message>

By default, all messages with a severity of `INFO` or above (`WARNING`, `ERROR` or `CRITICAL`) will reach stdout. In order to reduce the verbosity of the application, one can set `CST_STREAM_LOG_LEVEL` environment variable to a higher severity level i.e. setting `CST_STREAM_LOG_LEVEL=ERROR` will only display `ERROR` and `CRITICAL` log records.


Probably the less obvious section in the logger format above is the `operation_id` part. This is a custom logging attribute bound to the flask application context, more details about it in the RESOURCES section below.


##### RESOURCES 

ApiResource is an enhanced version of [Flask-RESTful's resource](https://flask-restful.readthedocs.io/en/latest/quickstart.html#resourceful-routing) building block.
One would use it in the same manner as a Flask-RESTful resource: 
```python
import logging
from flask import Flask
from flask_restful import Api

from cst_micro_chassis import CstMicroChassis
from cst_micro_chassis.resources import ApiResource

app = Flask('new-app')
CstMicroChassis().init_app(app)
logger = logging.getLogger(__name__)

api = Api(app)


class MySimpleResource(ApiResource):
    def get(self, simple_id):
        logger.info(f'I received a GET request for {simple_id}')
        return f'It works for {simple_id}'


api.add_resource(MySimpleResource, '/simple/<string:simple_id>')

if __name__ == '__main__':
    app.run(debug=True)

```

making a get request to this _"/simple"_ endpoint, will return :
```shell
curl localhost:5000/simple/123
{
    "meta": {
        "operation_id": "79bfcecd-55ba-4f97-b175-b104962cafa2"
    },
    "data": "It works for 123"
}
```
The most obvious difference (compared to a standard response expected from a flask-RESTful resource get method) is the response body, which has two main sections: `"meta"` and `"data"`. 

 - The `"data"` section contains the actual result of the get operation, which in our naive example, is adding the "It works for " prefix to the simple_id argument which has a value of 123.
 - The `"meta"` section contains by default an `operation_id`, which is a unique uuid4 identifier assigned to each http request. Also looking at flask servers logs, one can notice that between the log level `[INFO]` and the application name "new-app", also the logging entry's operation_id section was populated with the same value of `79bfcecd-55ba-4f97-b175-b104962cafa2`
   
    ```shell
    2021-01-01 11:35:01,419 [INFO][79bfcecd-55ba-4f97-b175-b104962cafa2] new-app: I received a GET request for 123
    ```
   
    This unique identifier eases debugging by allowing log grouping, aggregation and overall a better tracking on each operation made via the API endpoints.

 - More metadata can be added to this `meta` section, like: filtering, sorting or pagination params - as it will be detailed in the following section

   
##### PAGINATION

Assuming the application uses SQLAlchemy ORM, one can use the cst-micro-chassis pagination mixin like this:

```python
#assuming there is a model Product, which has at least a few tens of rows saved in db
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Product(db.Model):
    id = db.Column(db.String, unique=True, primary_key=True, default=lambda x: str(uuid4()))
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime)
```
creating a paginated endpoint to expose all these products, its as easy as: 
```python
from cst_micro_chassis.resources import ApiResource, ApiPaginatedMixin
class ProductsResource(ApiPaginatedMixin, ApiResource):
    def get(self):
        products = self.get_paginated_query_result(
            Product.query.order_by(Product.created_at.asc())
        )
        serialized = [{'name': p.name, 'created': p.created_at.isoformat()} for p in products]
        return serialized, 200
api = Api(app)
api.add_resource(ProductsResource, '/products')
```
Behind the scene, this will setup a basic pagination with a default of 25 items per page, which will automatically slice the results of `Product.query.order_by(Product.created_at.asc())` query , and populate the meta section in the response accordingly with a `next` and `prev` link:
`curl localhost/products/` will return
```json
{
    "meta": {
        "operation_id": "32013480-c882-46dd-a9d6-a931a8535cbe",
        "pagination": {
            "next": "http://localhost:5000/products/?offset=25&limit=25",
            "prev": null
        }
    },
    "data": [ ...]
}
```
The default number of items per page, which defaults to 25 , can be changed by setting the `CST_API_DEFAULT_PAGE_SIZE` environment variable.

Full code example for pagination (manual installation of flask_sqlalchemy is needed)
```python
#app.py
import datetime
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from cst_micro_chassis import CstMicroChassis
from cst_micro_chassis.resources import ApiResource, ApiPaginatedMixin

app = Flask('new-app')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
chassis = CstMicroChassis()

db.init_app(app)
chassis.init_app(app)

api = Api(app)


class Product(db.Model):
    id = db.Column(db.String, unique=True, 
                   primary_key=True, default=lambda x: str(uuid4()))
    name = db.Column(db.String)
    # ..
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

if __name__ == '__main__':
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

    app.run(debug=True)
```
---
#### Contributing
 - run the tests: 
```shell
make test
```
this will set up a virtual environment with [tox](https://tox.readthedocs.io) and run the unittest on Python3.9 

If one wants to run the test using a different interpreter version, one can use the pyversion argument for the `make` command like this:
`make pyversion=py38 test` (clearly, that interpreter version must be installed on the host otherwise tox will raise an `ERROR: InterpreterNotFound: python..` )
