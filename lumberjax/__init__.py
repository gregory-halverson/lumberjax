"""
This is a minimalistic thread-safe logger.

Gregory Halverson 2017
"""

from os.path import join, abspath, dirname
from .lumberjax import Logger

__author__ = 'Gregory Halverson'

logger = Logger()

with open(join(abspath(dirname(__file__)), "version.txt")) as f:
    __version__ = f.read()
