from logging import Formatter

try:
    # the logger might be used outside of flasks application context, don't always rely on flask.g
    from flask import g
except (ImportError, RuntimeError):
    g = None


class CstMicroChassisLogFormatter(Formatter):
    def format(self, record):
        # set the current operation_id for every log message formatted by this Formatter
        # alternatively, this could be done in the .format method of the Handler if we need it
        # regardless of the formatter used
        record.operation_id = g.operation_id if hasattr(g, 'operation_id') else 'No operation_id'
        return super(CstMicroChassisLogFormatter, self).format(record)
