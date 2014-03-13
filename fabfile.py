# -*- coding: utf-8 -*-
import os
import sys
import time

from fabric.api import local, hosts
from fabric.colors import green, red, yellow
from fabric.state import output as fab_output

from app.settings import local as settings

fab_output["running"] = False


def clean():
    """ Brise .pyc fileove """
    local("rm -rf `find . -type f -name '*.pyc'`")
    local("rm -rf `find . -type f -name 'debug.log'`")
    local("rm -rf `find . -type f -name '*.swp'`")


@hosts('localhost')
def start(port=None):
    """ Pokrece lokalni server """
    sys.path.append("./")
    from app.web import app
    if port:
        app.run(host="0.0.0.0", port=int(port), debug=settings.DEBUG)
    else:
        app.run(host="0.0.0.0", debug=settings.DEBUG)

def create_db():
    from app.web import db
    db.create_all()

def drop_db():
    from app.web import db
    db.drop_all()