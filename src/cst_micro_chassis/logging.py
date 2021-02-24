from logging import Formatter, config
import os

try:
    # the logger might be used outside of flasks application context, don't always rely on flask.g
    from flask import g
except (ImportError, RuntimeError):
    g = None


FORMAT = '%(asctime)s [%(levelname)s][%(operation_id)s] %(name)s: %(message)s'

STREAM_LOG_LEVEL = (
        os.environ.get('CST_STREAM_LOG_LEVEL') or
        os.environ.get('APP_STREAM_LOG_LEVEL') or  # legacy support
        'INFO'
).upper()
if STREAM_LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    import logging
    logging.getLogger(__name__).warning(
        'Invalid value for STREAM_LOG_LEVEL. The value was revised and set to INFO'
    )
    STREAM_LOG_LEVEL = 'INFO'


class CstMicroChassisLogFormatter(Formatter):
    def format(self, record):
        # set the current operation_id for every log message formatted by this Formatter
        # alternatively, this could be done in the .format method of the Handler if we need it
        # regardless of the formatter used
        try:
            record.operation_id = getattr(g, 'operation_id', None) or 'No operation_id'
        except (RuntimeError, AttributeError):
            record.operation_id = 'No operation_id'
        return super().format(record)


def get_log_config_dict(app_name):
    return {
        'version': 1,
        'formatters': {
            'standard': {
                'class': 'cst_micro_chassis.logging.CstMicroChassisLogFormatter',
                'format': FORMAT,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'DEBUG',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            app_name: {
                'handlers': ['console'],
                'propagate': False,
                'level': STREAM_LOG_LEVEL,
            },
        }
    }

