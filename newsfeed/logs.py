from backoff import expo
from backoff import on_exception
from logging import Formatter
from logging import getLogger
from logging import DEBUG
from logging.handlers import RotatingFileHandler
from sys import exc_info
from traceback import format_exception

# The format for local logs.
LOGS_FORMAT = ("%(asctime)s "
               "%(name)s "
               "%(process)d "
               "%(thread)d "
               "%(levelname)s "
               "%(message)s")

# The path to the log file for local logging.
LOG_FILE = "/tmp/main.log"

# The maximum size in bytes for each local log file.
MAX_LOG_BYTES = 10 * 1024 * 1024

class Logs:
    """A helper for logging locally."""

    def __init__(self, name):
        # Initialize the local file logger.
        self.local_logger, _ = self.get_local_logger(name, LOG_FILE)

    def get_local_logger(self, name, log_file):
        """Returns a local logger with a file handler."""

        handler = RotatingFileHandler(log_file, maxBytes=MAX_LOG_BYTES)
        handler.setFormatter(Formatter(LOGS_FORMAT))
        handler.setLevel(DEBUG)

        logger = getLogger(name)
        logger.setLevel(DEBUG)
        logger.handlers = [handler]

        return (logger, handler)

    def debug(self, text):
        """Logs at the DEBUG level."""

        self.local_logger.debug(text)

    def info(self, text):
        """Logs at the INFO level."""

        self.local_logger.info(text)

    def warn(self, text):
        """Logs at the WARNING level."""
        
        self.local_logger.warning(text)

    def error(self, text):
        """Logs at the ERROR level."""

        self.local_logger.error(text)

    def catch(self):
        """Logs the latest exception."""

        exception_str = self.format_exception()
        self.local_logger.critical(exception_str)

    def safe_report_exception(self, exception_str):
        """Reports the exception, retries if necessary, and eventually fails
        over to local logs.
        """
        try:
            self.retry_report_exception(exception_str)
        except Exception:
            meta_exception_str = self.format_exception()
            self.fallback_logger.error("Failed to report exception: %s\n%s" %
                                       (exception_str, meta_exception_str))

    @on_exception(expo, Exception, max_tries=8)
    def retry_report_exception(self, exception_str):
        """Reports the exception and retries up to 10 times with exponential
        backoff (51.2 seconds max total) if the upload fails.
        """

        self.error_client.report(exception_str)

    def format_exception(self):
        """Grabs the latest exception and formats it."""

        exc_type, exc_value, exc_traceback = exc_info()
        exc_format = format_exception(exc_type, exc_value, exc_traceback)
        return "".join(exc_format).strip()
