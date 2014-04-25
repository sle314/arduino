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

    from app.helpers.request_helper import init_pin_modes
    init_pin_modes()


def create_db():
    """ Stvara bazu podataka """
    from app.web import db
    db.create_all()

def drop_db():
    """ Brise bazu podataka """
    from app.web import db
    db.drop_all()

def init_db():
    """
    inicijalizira bazu podataka
    prije koristenja potrebno je zakomentirati zadnje tri linije u datoteci app/web/__init__.py
    """
    from app.arduino.hardware import Hardware, Module, Pin, Method

    for h in settings.HARDWARE:
        hw = Hardware(h['name'], h['path'])
        hw.save()

        for module in h['modules']:
            module['hw_id'] = hw.id
            m = Module( module )
            m.save()

            for method in module['methods']:
                method['mod_id'] = m.id
                meth = Method( method )
                meth.save()

        for pin in h['pins']:
            pin['hw_id'] = hw.id
            p = Pin( pin )
            p.save()

