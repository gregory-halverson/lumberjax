import json
from os.path import join, abspath, dirname

from setuptools import setup, find_packages

__author__ = 'Gregory Halverson'

NAME = 'lumberjax'
URL = 'http://www.github.com/gregory-halverson/lumberjax'
AUTHOR_EMAIL = 'gregory.halverson@gmail.com'
DESCRIPTION = 'Minimimalistic, Thread-Safe Logger'
LICENSE = 'MIT'

with open(join(NAME, 'version.txt')) as f:
    version = str(f.read())

with open(join(abspath(dirname(__file__)), 'requirements.txt'), 'r') as f:
    install_requires = f.readlines()

with open(join(abspath(dirname(__file__)), 'packagedata.json'), 'r') as f:
    package_data = json.loads(f.read())

packages = find_packages(where='.', exclude=())

setup(
    name=NAME,
    version=version,
    packages=packages,
    package_data=package_data,
    install_requires=install_requires,
    url=URL,
    license=LICENSE,
    author=__author__,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION
)
