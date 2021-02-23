import os
from uuid import uuid4
from flask import g, request
from flask_restful import Resource

try:
    API_DEFAULT_PAGE_SIZE = int(os.environ.get('CST_API_DEFAULT_PAGE_SIZE'))
except (TypeError, ValueError):
    API_DEFAULT_PAGE_SIZE = 25


class ApiResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = []
        # pagination disabled by default
        self.enable_pagination = False

    def add_error(self, message, path=None):
        err = dict(message=message)
        if path:
            err['path'] = path
        self.errors.append(err)

    def dispatch_request(self, *args, **kwargs):
        self.errors = []
        if not getattr(g, 'operation_id', None):
            g.operation_id = str(uuid4())
        new_response = {'meta': {'operation_id': str(g.operation_id)}}

        if self.enable_pagination:
            self._set_pagination_attributes()

        if self.errors:
            new_response['errors'] = self.errors
            return new_response, 400

        status_code = None
        response = super().dispatch_request(*args, **kwargs)
        if isinstance(response, (list, tuple)):
            response, status_code = response

        if self.errors:
            new_response['errors'] = self.errors
        else:
            new_response['data'] = response
            if self.enable_pagination:
                new_response = self._add_pagination_meta(new_response)

        return new_response, status_code if status_code else response


class ApiPaginatedMixin:
    def __init__(self):
        super().__init__()
        self.enable_pagination = True
        self.has_next = False
        self.offset = 0
        self.limit = API_DEFAULT_PAGE_SIZE

    def get_paginated_query_result(self, query):
        result_list = self.apply_limits_to_query(query).all()
        return self.compute_has_next(result_list)

    def apply_limits_to_query(self, query):
        """
        IMPORTANT always call self.compute_has_next(query.all()) on the results of this query !!!
        :param query: SQLAlchemy BaseQuery object to be sliced on db side according to self.offset
         and/or self.limit
        :return: SQLAlchemy BaseQuery object with a limit / offset sql clause added
        """
        if self.offset:
            query = query.offset(self.offset)
        if self.limit:
            # fetching an extra item, to be able to compute self.has_next
            # the extra item will be removed when calling self.compute_has_next
            query = query.limit(self.limit + 1)
        return query

    def compute_has_next(self, items):
        """
        Checks if number of items is equal to self.limit + 1 -> self.has_next = true
        cannot be directly called by apply_limits_to_query because it will force the evaluation of
        the query and the user of that function may not want it because he may have other filters
        /sorting/sub-queries needed to add to this query.
        :param items: list of items that need to be paginated
        :return: list of items without the last item in the list - which was requested only to see
        if there are more items than needed meaning the `next` url in meta should be displayed
        """
        if items and len(items) == self.limit + 1:
            self.has_next = True
            del items[-1]
        return items

    def _set_pagination_attributes(self):
        _offset = request.args.get('offset')
        _limit = request.args.get('limit')
        try:
            if _offset:
                self.offset = int(_offset)
                if self.offset < 0:
                    raise ValueError
        except ValueError:
            self.add_error(f"Invalid parameter 'offset={_offset}'")
        try:
            if _limit:
                self.limit = int(_limit)
                if self.limit < 0 or self.limit > 4 * API_DEFAULT_PAGE_SIZE:
                    # max page size = 4*default page size
                    raise ValueError
        except ValueError:
            self.add_error(f"Invalid parameter 'limit={_limit}'")

    def _add_pagination_meta(self, response):
        # store the existing query parameters in order to avoid losing any filters
        request_args = dict(request.args)

        next_url = None
        if self.has_next:
            request_args['offset'] = self.offset + self.limit
            request_args['limit'] = self.limit
            next_url = f'{request.base_url}?{"&".join(f"{k}={v}" for k, v in request_args.items())}'

        prev_url = None
        if self.offset > 0:
            request_args['offset'] = max(self.offset - self.limit, 0)
            request_args['limit'] = self.limit
            prev_url = f'{request.base_url}?{"&".join(f"{k}={v}" for k, v in request_args.items())}'

        response['meta']['pagination'] = {
            'next': next_url,
            'prev': prev_url,
        }

        return response
