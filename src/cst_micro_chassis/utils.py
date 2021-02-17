import time
import logging

from functools import wraps


logger = logging.getLogger(__name__)


def retry(tries=3, delay=2, back_off=2, custom_logger=None):
    """
    Retry calling the decorated function until getting non-falsy results.
    :param tries: Number of times to try (not retry) before giving up.
    :param delay: Initial delay between retries in seconds.
    :param back_off: Back-off multiplier (e.g. value of 2 will double the delay each retry).
    :param custom_logger: Logger to use. If None, use the one available in this module .
    """
    custom_logger = custom_logger or logger

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            remaining_tries, current_delay = tries, delay
            result = None
            while True:
                try:
                    result = f(*args, **kwargs)
                except Exception as ex:
                    if remaining_tries <= 1:
                        raise ex
                    custom_logger.warning(
                        f'An exception was raised when executing {f.__name__}:{ex}')
                remaining_tries -= 1

                if result or remaining_tries < 1:
                    break
                current_delay *= back_off
                custom_logger.info(f'Retrying {f.__name__} in {current_delay} sec ...')
                time.sleep(current_delay)
            return result
        return f_retry  # true decorator
    return deco_retry
