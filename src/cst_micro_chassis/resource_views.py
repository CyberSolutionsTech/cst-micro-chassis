from uuid import uuid4
from flask import g
from flask_restful import Resource


class ChassisResourceView(Resource):
    def __init__(self, *args, **kwargs):
        super(ChassisResourceView, self).__init__(*args, **kwargs)
        self.errors = []

    def add_error(self, message, path=None):
        err = dict(message=message)
        if path:
            err['path'] = path
        self.errors.append(err)

    def dispatch_request(self, *args, **kwargs):
        self.errors = []
        g.operation_id = uuid4()
        new_response = {'meta': {'operation_id': str(g.operation_id)}}

        if self.errors:
            new_response['errors'] = self.errors
            return new_response, 400

        status_code = None
        response = super(ChassisResourceView, self).dispatch_request(*args, **kwargs)
        if isinstance(response, (list, tuple)):
            response, status_code = response

        if self.errors:
            new_response['errors'] = self.errors
        else:
            new_response['data'] = response

        return new_response, status_code if status_code else response
