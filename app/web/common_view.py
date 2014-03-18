# -*- coding: utf-8 -*-
from . import app
from app.settings import local as settings
import os

from flask import render_template, request, session, redirect, flash
from requests.exceptions import ConnectionError, Timeout
from app.arduino.sensor import SensorInteractor
from app.arduino.gateway import GatewayInteractor
import xml.etree.ElementTree as ET
import requests

@app.before_request
def before_request():
    if request.endpoint != "static":
        if 'gateway' not in session:
            print "Here"
            session['gateway'] = settings.GATEWAY
            from app.helpers.base64_helper import b64encode_quote
            session['auth'] = b64encode_quote(settings.AUTH)
            session['post-auth'] = b64encode_quote(settings.POST_AUTH)
            session['error'] = True
            session['registered'] = False


@app.route('/')
def index():
    return render_template("gateway/index.html", settings=settings, gateways=GatewayInteractor.get_all())


@app.route('/register/')
def register():
    if not session['error']:
        return render_template('device/register.html')
    else:
        flash('Gateway error!', category={ 'theme': 'error' } )
        return redirect('/')

@app.route('/unregister/')
def unregister():
    return redirect('register')


@app.route('/remove_device/')
def remove_device():

    headers = {'Authorization': 'Basic %s' % session['post-auth']}

    r = requests.delete("%s%s/%s" % (
                session['gateway'],
                settings.APPLICATIONS,
                settings.DEVICE_ID
            ),
            headers = headers,
            timeout = 5
        )

    if r.status_code == 204:
        flash('Device successfully removed from gateway!', category={ 'theme': 'success' } )
        session['registered'] = False
        for sensor in SensorInteractor.get_all():
            sensor.registered = 0
            sensor.save()
    elif r.status_code == 404:
        flash('Device is already removed!', category={ 'theme': 'warning' } )
        session['registered'] = False
        for sensor in SensorInteractor.get_all():
            sensor.registered = False
            sensor.save()
    else:
        flash('Something went wrong!', category={ 'theme': 'error' } )
    return redirect('/register/')


@app.route('/register_device/')
def register_device():

    ET.register_namespace("m2m", "http://uri.etsi.org/m2m")
    tree = ET.parse('%s/app/web/xml/device.xml' % os.getcwd())

    root = tree.getroot()
    root.set('appId', settings.DEVICE_ID)

    search_string = ET.SubElement(root, 'm2m:searchString')
    search_string.text = 'ETSI.ObjectTechnology/ACTILITY.%s' % settings.DEVICE_ID

    headers = {'Authorization': 'Basic %s' % session['post-auth'], "content-type":"application/xml"}

    try:
        r = requests.post("%s%s" % (
                    session['gateway'],
                    settings.APPLICATIONS
                ),
                headers = headers,
                timeout = 5,
                data = ET.tostring(root)
            )

        if r.status_code == 201 or r.status_code == 409:

            tree = ET.parse('%s/app/web/xml/device_descriptor.xml' % os.getcwd())

            r = requests.post("%s%s/%s%s" % (
                    session['gateway'],
                    settings.APPLICATIONS,
                    settings.DEVICE_ID,
                    settings.CONTAINERS
                ),
                headers = headers,
                timeout = 5,
                data = ET.tostring(tree.getroot())
            )

            flash('Device successfully registered!', category={ 'theme': 'success' } )
            session['registered'] = True

        elif r.status_code == 400 or r.status_code == 401:
            flash('Wrong authorization for registration!', category={ 'theme': 'error' } )

        else:
            flash('Something went wrong!', category={ 'theme': 'error' } )

    except ConnectionError:
        flash("Cannot connect to specified gateway!", category={ 'theme': 'error' } )

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )

    return redirect('/register/')
