import pytest

from cst_micro_chassis.utils import retry
from unittest import mock


class SomeTestClass:
    def __init__(self):
        self.wrapped_test_function_called_count = 0

    @retry(delay=1)
    def wrapped_test_function(self, argument):
        self.wrapped_test_function_called_count += 1
        if argument == 'tr':
            return True
        elif argument == 'null div':
            return 2 / 0
        return 0


def test_wrapped_function_works_first_call():
    stc = SomeTestClass()
    result = stc.wrapped_test_function('tr')
    assert result is True
    assert stc.wrapped_test_function_called_count == 1


# mocking time sleep, so we don't wait the seconds between tries
@mock.patch('cst_micro_chassis.utils.time.sleep', return_value=None)
def test_wrapped_function_falsy_result_retried(_):
    stc = SomeTestClass()
    result = stc.wrapped_test_function('something_else')
    assert result == 0
    assert stc.wrapped_test_function_called_count == 3


@mock.patch('cst_micro_chassis.utils.time.sleep', return_value=None)
def test_wrapped_function_retries_default_three_times(_):
    with pytest.raises(ZeroDivisionError) as _:
        stc = SomeTestClass()
        stc.wrapped_test_function('null div')
    assert stc.wrapped_test_function_called_count == 3
