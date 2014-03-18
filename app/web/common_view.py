# -*- coding: utf-8 -*-
from . import app
from app.settings import local as settings
import os

from flask import render_template, request, session, redirect, flash
from requests.exceptions import ConnectionError, Timeout
from app.arduino.sensor import SensorInteractor
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
    return render_template("index.html")


@app.route('/set_gateway/', methods=['POST'])
def set_gateway():

    gateway = request.form.get("gateway")
    gateway = gateway if "http://" in gateway else "http://%s" % gateway

    from app.helpers.base64_helper import b64encode_quote
    auth = b64encode_quote(request.form.get("auth"))

    headers = {'Authorization': 'Basic %s' % auth}

    try:

        r = requests.get("%s%s" % (
                gateway,
                settings.ACCESS_RIGHTS
            ),
            headers = headers,
            timeout = 5
        )

        if r.status_code == 200:
            session['error'] = False
            root = ET.fromstring(r.text)

            if root:
                session['post-auth'] = b64encode_quote(root[4][0][1][0][1].text)
                session['gateway'] = gateway
                session['auth'] = auth

                r = requests.get("%s%s/%s" % (
                        gateway,
                        settings.APPLICATIONS,
                        settings.DEVICE_ID
                    ),
                    headers = headers,
                    timeout = 5
                )

                if r.status_code == 200:
                    session['registered'] = True
                    flash("Gateway set!", category='success')
                    flash("Device is already registered!", category='success')
                    return redirect("/sensors/")

                elif r.status_code == 404:
                    flash("Device is not registered.", category='warning')
                    return redirect("/register/")
            else:
                flash('Response was not a valid accessRights XML!', category='error')

        elif r.status_code == 400 or r.status_code == 404:
            flash('Wrong authorization URI!', category='error')

    except ConnectionError:
        flash("Cannot connect to specified gateway!", category='error')

    except Timeout:
        flash("Request timed out. Wrong IP?", category='error')

    session['error'] = True
    return redirect('/')



@app.route('/register/')
def register():
    if not session['error']:
        return render_template('device/register.html')
    else:
        flash('Gateway error!', category='error')
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
        flash('Device successfully removed from gateway!', category='success')
        session['registered'] = False
        for sensor in SensorInteractor.get_all():
            sensor.registered = 0
            sensor.save()
    elif r.status_code == 404:
        flash('Device is already removed!', category='warning')
        session['registered'] = False
        for sensor in SensorInteractor.get_all():
            sensor.registered = False
            sensor.save()
    else:
        flash('Something went wrong!', category='error')
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

            flash('Device successfully registered!', category='success')
            session['registered'] = True

        elif r.status_code == 400 or r.status_code == 401:
            flash('Wrong authorization for registration!', category='error')

        else:
            flash('Something went wrong!', category='error')

    except ConnectionError:
        flash("Cannot connect to specified gateway!", category='error')

    except Timeout:
        flash("Request timed out. Wrong IP?", category='error')

    return redirect('/register/')
