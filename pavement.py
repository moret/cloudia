# coding: utf-8
from __future__ import absolute_import

import sys
sys.path = ['.'] + sys.path
import pexpect

from paver.easy import task, cmdopts, sh
from paver.tasks import help
import pytest

from web import server
from model.settings import settings

@task
def tests():
    clean()
    settings.MOCK_GROUP_MANAGER = True
    test_server = pexpect.spawn('paver run')
    test_server.expect(' => Listening on 8888')

    pytest.main('-s -v tests')

    test_server.terminate()
    clean()

@task
def run():
    clean()
    server.start()
    clean()

@task
def clean():
    sh('find . -name "__pycache__" -delete')
    sh('find . -name "*.pyc" -delete')
    sh('find . -name "*~" -delete')
