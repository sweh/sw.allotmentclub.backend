from __future__ import unicode_literals

import datetime
import logging

import user_agents

from .model import Log

STRIP_CHARS = "\n\r\f<:"


class UserRequestLogger(logging.LoggerAdapter):
    def __init__(self, logger):
        """Overwrite init so we do not require the dict used for extra args."""
        super(UserRequestLogger, self).__init__(logger, {})

    def __getattr__(self, name):
        """Forward unknown calls to the logger. Required for testing setup."""
        return getattr(self.logger, name)

    def process(self, msg, kwargs):
        """Enrich log msg with IP address and browser used for current request.

        Can be disabled by adding `log_request=False` as kwarg to log call.
        """
        import pyramid.threadlocal

        request = pyramid.threadlocal.get_current_request()

        if request is None or not kwargs.pop("log_request", True):
            return msg, kwargs

        ip_address = request.environ.get("HTTP_X_REAL_IP")
        if ip_address is None and hasattr(request, "client_addr"):
            ip_address = request.client_addr
        user_agent_header = request.environ.get("HTTP_USER_AGENT")
        browser = "no useragent sent"
        if user_agent_header is not None:
            user_agent = user_agents.parse(user_agent_header)
            family = user_agent.browser.family
            version = user_agent.browser.version_string
            browser = family
            if version:
                browser = browser + " " + version

        return "{} [IP:{}] [Browser:{}]".format(
            msg, ip_address, browser
        ), kwargs


app_log = logging.getLogger("app")
client_log = UserRequestLogger(logging.getLogger("client"))
auth_log = UserRequestLogger(logging.getLogger("auth"))
error_log = UserRequestLogger(logging.getLogger("error"))
user_admin_log = UserRequestLogger(logging.getLogger("user admin"))
user_data_log = UserRequestLogger(logging.getLogger("user data"))


def log_with_user(log, user, *args, **kwargs):
    """Use this function to log into database, too."""
    kwargs["extra"] = {"user": user}
    return log(*args, **kwargs)


def _strip(obj):
    """Strip chars which should not be in log file due to app-12.1.6."""
    return obj.translate(None, STRIP_CHARS)


class TruncatingLogRecord(logging.LogRecord):
    """Truncating log message to a maximum value defined in environment.

    Environment key is `LOG_RECORD_MAX_LEN`.
    If not set it defaults to unlimited.

    """

    _record_max_len = None

    def getMessage(self):
        msg = super(TruncatingLogRecord, self).getMessage()
        if self._record_max_len and len(msg) > self._record_max_len:
            ellisis = "…"
            msg = msg[0 : self._record_max_len] + ellisis
        return msg


class TruncatingLogAndStrippingArgsRecord(TruncatingLogRecord):
    def getMessage(self):
        self._strip_args()
        return super(TruncatingLogAndStrippingArgsRecord, self).getMessage()

    def _strip_args(self):
        if isinstance(self.args, tuple):
            self.args = tuple(x for x in self.args)
        if isinstance(self.args, dict):
            self.args = {k: v for k, v in self.args.items()}


class StreamHandler(logging.StreamHandler):
    """Custom stream handler which truncates log record."""

    def __init__(self, stream=None, record_max_len=0):
        super(StreamHandler, self).__init__(stream)
        self._record_max_len = int(record_max_len)

    def emit(self, record):
        # Switch the record to a TruncatingLogAndStrippingArgsRecord:
        record.__class__ = TruncatingLogAndStrippingArgsRecord
        record._record_max_len = self._record_max_len
        return super(StreamHandler, self).emit(record)


class DBHandler(logging.Handler):
    """Handler to log user related activity in the database"""

    def __init__(self, record_max_len=0):
        super(DBHandler, self).__init__()
        self._record_max_len = int(record_max_len)

    def emit(self, record):
        # Switch the record to a TruncatingLogRecord:
        record.__class__ = TruncatingLogRecord
        record._record_max_len = self._record_max_len
        user = getattr(record, "user", None)
        if not user:
            return  # will skip all non-user centric logs like errors, SQL etc.
        message = record.getMessage()
        created = datetime.datetime.fromtimestamp(record.created)
        level = record.levelname
        name = record.name
        Log.create(
            msg=message,
            user=user,
            created=created,
            level=level,
            name=name,
            organization_id=user.organization_id,
        )
