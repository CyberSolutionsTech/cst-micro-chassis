from cst_micro_chassis.resources import ApiResource, ApiPaginatedMixin


def test_resources_simple():
    ApiResource()
    ApiPaginatedMixin()
