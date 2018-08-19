"""
This is a minimalistic thread-safe logger.

Gregory Halverson 2017
"""

import re
import sys
import traceback
from datetime import datetime
from os import makedirs
from os.path import exists, join

from six import StringIO, string_types
from termcolor import colored

__author__ = 'Gregory Halverson'

DEFAULT_STDOUT = sys.stdout
DEFAULT_STDERR = sys.stdout


def print_traceback(device):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback, file=device)


def traceback_string():
    device = StringIO()
    print_traceback(device)
    tb = device.getvalue()
    device.close()

    if tb == 'NoneType\n':
        return None
    else:
        return tb


class DummyLock(object):
    def __enter__(self):
        pass

    def __exit__(self, exception_type, exception_value, exception_traceback):
        pass


class Logger(object):
    """
    This is a minimalistic thread-safe logger.
    """

    _ansi_escape = re.compile(r'\x1b[^m]*m')

    def __init__(
            self,
            stdout_categories=('INFO'),
            stderr_categories=('ERROR', 'WARN', 'CRITICAL'),
            log_directory=None,
            lock=None,
            datetime_format='%Y-%m-%d %H:%M:%S'):

        self.stdout_categories = stdout_categories
        self.stderr_categories = stderr_categories

        if lock is None:
            self.lock = DummyLock()
        else:
            self.lock = lock

        self.datetime_format = datetime_format
        self.log_directory = log_directory
        self.start_time = datetime.now()

        if self.log_directory is not None:
            self.info("logger writing to '{}'".format(self.log_directory))

    @property
    def stdout(self):
        return DEFAULT_STDOUT

    @property
    def stderr(self):
        return DEFAULT_STDERR

    def filename(self, category):
        return join(self.log_directory, "{:04d}.{:02d}.{:02d}.{:02d}.{:02d}.{}.txt".format(
            self.start_time.year,
            self.start_time.month,
            self.start_time.day,
            self.start_time.hour,
            self.start_time.minute,
            category
        ))

    def attach(self, lock=None):
        if lock is not None:
            self.lock = lock

    def load_settings_dict(self, settings):
        if 'stdout_categories' in settings:
            self.stdout_categories = settings['stdout_categories']

        if 'stderr_categories' in settings:
            self.stderr_categories = settings['stderr_categories']

        if 'datetime_format' in settings:
            self.datetime_format = settings['datetime_format']
            # self.verbose("datetime_format: {}".format(self.datetime_format))

    def _strip(self, ansi):
        return self._ansi_escape.sub('', ansi)

    def _timestamp(self, category):
        return "[{} {}]".format(
            datetime.now().strftime(self.datetime_format),
            category
        )

    def _print(self, message, category):
        if self.stdout is None:
            return

        if self.stdout_categories is not None and category not in self.stdout_categories:
            return

        if not isinstance(message, string_types):
            message = str(message)

        if self.lock is None:
            self.lock = DummyLock()

        with self.lock:
            self.stdout.flush()
            self.stderr.flush()

            for line in message.split('\n'):
                self.stdout.write('{} {}\n'.format(
                    self._timestamp(category),
                    line
                ))

            self.stdout.flush()

    def _print_stderr(self, message, category):
        if self.stderr is None:
            return

        if not (self.stderr_categories is None or category in self.stderr_categories):
            return

        if not isinstance(message, string_types):
            message = str(message)

        self.stderr.flush()

        for line in message.split('\n'):
            self.stderr.write(colored('{} {}\n', 'red').format(
                self._timestamp(category),
                self._strip(line)
            ))

        self.stderr.flush()

    def _write(self, message, category):
        if self.log_directory is None:
            return

        if not isinstance(message, string_types):
            message = str(message)

        if self.lock is None:
            self.lock = DummyLock()

        with self.lock:
            if not exists(self.log_directory):
                try:
                    makedirs(self.log_directory)
                except OSError as e:
                    self.warn(e)

            with open(self.filename(category), 'a') as log_file:
                for line in self._strip(message).split('\n'):
                    log_file.write('{} {}\n'.format(
                        self._timestamp(category),
                        line
                    ))

    def _write_error(self, message, category):
        if self.log_directory is None:
            return

        if not isinstance(message, string_types):
            message = str(message)

        with open(self.filename(category), 'a') as log_file:
            for line in self._strip(message).split('\n'):
                log_file.write('{} {}\n'.format(
                    self._timestamp(category),
                    line
                ))

    def _message(self, message, category):

        if not isinstance(message, string_types):
            message = str(message)

        self._print(message, category)
        self._write(message, category)

    def _message_error(self, message, category):

        if not isinstance(message, string_types):
            message = str(message)

        self._print_stderr(message, category)
        self._write_error(message, category)

    def info(self, message):
        """
        Log an info message.
        """

        if not isinstance(message, string_types):
            message = str(message)

        self._message(message, 'INFO')

    def warn(self, message):
        """
        Log a warning.
        """
        if not isinstance(message, string_types):
            message = str(message)

        self._message_error(message, 'WARN')

    def verbose(self, message):
        """
        Log a verbose message.
        """

        if not isinstance(message, string_types):
            message = str(message)

        self._message(message, 'VERBOSE')

    def debug(self, message):
        """
        Log a debug message.
        """

        if not isinstance(message, string_types):
            message = str(message)

        self._message(message, 'DEBUG')

    def error(self, message=None):
        """
        Log an error message.
        """

        if not isinstance(message, string_types):
            message = str(message)

        tb = traceback_string()

        if tb:
            if message is None:
                message = tb
            else:
                message = '\n'.join((tb, message))

        self._message_error(message, 'ERROR')

    def critical(self, message):
        """
        Log a critical message.
        """

        self.lock = DummyLock()

        if not isinstance(message, string_types):
            message = str(message)

        self._message_error(message, 'CRITICAL')
