# -*- coding: utf-8 -*-
import os
import sys
import time

from fabric.api import hosts, local
from fabric.state import output as fab_output

from app.settings import local as settings

fab_output["running"] = False

def clean():
    """ Brise .pyc fileove """
    local("rm -rf `find . -type f -name '*.pyc'`")
    local("rm -rf `find . -type f -name 'debug.log'`")
    local("rm -rf `find . -type f -name '*.swp'`")


@hosts('localhost')
def start(port=5000):
    """ Pokrece lokalni posluzitelj """
    sys.path.append("./")

    from app.web import app
    from app.helpers.request_helper import init_pin_modes

    app.logger.info("-/-/-/-START FLASK APP START-/-/-/-")

    init_pin_modes()

    if settings.ENV in ["test","arduino"]:
        app.run(host=settings.SERVER_IP, port=int(settings.PORT), debug=settings.DEBUG)
    else:
        from subprocess import call
        call("gunicorn -b %s:%s -w %d app.web:app" % (settings.SERVER_IP, settings.PORT, settings.WORKERS), shell=True)

    app.logger.info("-/-/-/-END FLASK APP START-/-/-/-")


def backup_db(name=None):
    """ Backupira bazu podataka """
    if not name:
        name = raw_input("Please enter a filename (default arduino.db.bkp): ")
        if not name:
            name = "arduino.db.bkp"

    import shutil
    shutil.copy("app/db/arduino.db", "app/db/%s" % name)


def restore_db(name=None):
    """ Restorea bazu podataka """
    if not name:
        name = raw_input("Please enter a filename (default arduino.db.bkp): ")
        if not name:
            name = "arduino.db.bkp"
    import shutil
    shutil.copy("app/db/%s" % name, "app/db/arduino.db")


def reinit_db():
    """ Reinicijaliyira bazu podataka """
    drop_db()
    create_db(True)


def create_db(reinit=False):
    """ Stvara bazu podataka """
    if not reinit:
        val = raw_input("Do you want to restore the db? (y/n) ")
        if val and val != "n":
            val2 = raw_input("Please enter a name (default arduino.db.bkp): ")
            if not val2:
                val2 = "arduino.db.bkp"
            restore_db(val2)
        else:
            from app.web import db
            db.create_all()
            init_db()
    else:
        from app.web import db
        db.create_all()
        init_db()


def drop_db():
    """ Brise bazu podataka i pita da li ju prethodno zelimo spremiti """
    val = raw_input("Do you want to backup the db? (y/n) ")
    if val and val != "n":
        val2 = raw_input("Please enter a name (default arduino.db.bkp): ")
        if not val2:
            val2 = "arduino.db.bkp"
        backup_db(val2)

    from app.web import db
    db.drop_all()


def init_db():
    """
    Inicijalizira podatke u bazi za uredaj i module
    settings.INIT je postavljen zbog ciklickih ovisnosti
    """
    settings.INIT = True
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

    get_ip()


def get_ip():
    import json
    from app.arduino.common import PublicIPInteractor
    from urllib2 import urlopen
    ip = PublicIPInteractor.get()
    currentIP = json.load(urlopen('http://httpbin.org/ip'))['origin'].rstrip()
    ip.address = "%s:%s" % (currentIP, settings.PORT)
    ip.save()
