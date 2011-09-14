# coding: utf-8
from __future__ import absolute_import

import sys
sys.path = ['.'] + sys.path
import pexpect

from paver.easy import task, cmdopts, sh
from paver.tasks import help
import pytest

from web import server

@task
def tests():
    clean()
    test_server = pexpect.spawn('paver run')
    test_server.expect(' => Listening on 8888')

    pytest.main('-x tests')

    test_server.terminate()
    clean()

@task
def run():
    clean()
    server.start()
    clean()

@task
def clean():
    sh('find . -name "*.pyc" -delete')
    sh('find . -name "*~" -delete')