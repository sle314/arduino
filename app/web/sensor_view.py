# -*- coding: utf-8 -*-
from . import app
from flask import render_template, request, session, redirect, flash
from sqlalchemy.exc import IntegrityError
import xml.etree.ElementTree as ET
import os
from app.settings import local as settings
import requests

from app.arduino.sensor import Sensor, SensorInteractor


@app.route('/sensors/', methods=['GET'])
def get_sensors():
    sensors = SensorInteractor.get_all()
    return render_template("sensor/index.html", sensors = sensors )


@app.route('/sensors/', methods=['POST'])
def store_sensor():
    sensor = Sensor()

    for (key, value) in request.form.iteritems():
        if key == 'identificator' and value == "":
            flash('You left the identificator blank, try again!', category='error')
            return redirect('/sensors/add/')
        setattr(sensor, key, value.lower().replace(" ", "_") if key=="identificator" else value.replace(" ", "_"))
    try:
        sensor.save()
        flash("Sensor added!", category='success')
        return redirect("/sensors/%d/register/" % sensor.id)
    except IntegrityError:
        flash("Sensor with same identifier already exists!", category='error')
        return render_template("sensor/add.html", sensor=sensor)


@app.route('/sensors/<int:sensor_id>/', methods=['POST'])
def update_sensor(sensor_id):
    identificator_changed = False
    identificator = request.form.get("identificator").lower().replace(" ", "_")
    old_sensor = SensorInteractor.get(sensor_id)
    sensor = SensorInteractor.get_by_identificator(identificator)

    if old_sensor:
        if sensor and sensor != old_sensor:
            flash("Sensor with same identifier already exists!", category='warning')
            return redirect("/sensors/%d/edit/" % sensor_id)

        if old_sensor.identificator != identificator:
            identificator_changed = True
            unregister_sensor(sensor_id)

        for (key, value) in request.form.iteritems():
            setattr(old_sensor, key, value.lower().replace(" ", "_") if key=="identificator" else value.replace(" ", "_"))

        old_sensor.save()

        if identificator_changed:
            register_sensor(sensor_id)
        else:
            sensor_send_value(sensor_id)

        flash("Sensor edited!", category='success')
        return redirect("/sensors/")
    else:
        flash("Sensor doesn't exist!", category='error')
        return redirect("/sensors/")


@app.route('/sensors/<int:sensor_id>/edit/')
def edit_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)
    return render_template("/sensor/add.html", sensor = sensor)


@app.route('/sensors/add/')
def add_sensor():
    return render_template("sensor/add.html")


@app.route('/sensors/delete/', methods=['POST'])
def delete_sensor():
    sensor_id = request.form.get('sensor_id')

    sensor = SensorInteractor.get(sensor_id)

    if sensor:
        if sensor.registered:
            ET.register_namespace("m2m", "http://uri.etsi.org/m2m")

            headers = {'Authorization': 'Basic %s' % session['post-auth']}

            r = requests.delete("%s%s/%s%s/%s" % (
                    session['gateway'],
                    settings.APPLICATIONS,
                    settings.DEVICE_ID,
                    settings.CONTAINERS,
                    sensor.identificator
                ),
                headers = headers,
                timeout = 5
            )

            if r.status_code == 204:
                if SensorInteractor.delete(sensor_id):
                    flash("Sensor deleted!", category="success")
                else:
                    flash("Sensor was deleted on gateway but not locally!", category='error')
            else:
                flash("Sensor could not be deleted on gateway!", category='error')
        else:
            if SensorInteractor.delete(sensor_id):
                flash("Sensor deleted!", category='success')
            else:
                flash("Sensor could not be deleted!", category='error')
    else:
        flash('Sensor does not exist!', category='error')

    return redirect("/sensors/")

@app.route('/sensors/<int:sensor_id>/unregister/')
def unregister_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)

    if sensor:
        headers = {'Authorization': 'Basic %s' % session['post-auth']}

        r = requests.delete("%s%s/%s%s/%s" % (
                session['gateway'],
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS,
                sensor.identificator
            ),
            headers = headers,
            timeout = 5
        )

        print r.status_code

        if r.status_code == 204:
            sensor.registered = 0
            sensor.save()
            flash("Sensor was removed from gateway!", category='success')
        elif r.status_code == 404:
            sensor.registered = 0
            sensor.save()
            flash("Sensor was already removed!", category='warning')
        else:
            flash("Sensor could not be removed!", category='error')
    else:
        flash('Sensor does not exist!', category='error')

    return redirect("/sensors/")


@app.route('/sensors/<int:sensor_id>/register/')
def register_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)

    print sensor.identificator

    if sensor:
        ET.register_namespace("m2m", "http://uri.etsi.org/m2m")
        tree = ET.parse('%s/app/web/xml/sensor.xml' % os.getcwd())
        root = tree.getroot()

        root.set('m2m:id', sensor.identificator)
        root[2].text = str(settings.MAX_NR_VALUES)

        headers = {'Authorization': 'Basic %s' % session['post-auth'], "content-type":"application/xml"}

        r = requests.post("%s%s/%s%s" % (
                session['gateway'],
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS
            ),
            headers = headers,
            timeout = 5,
            data = ET.tostring(root)
        )

        tree = ET.parse('%s/app/web/xml/sensor_value.xml' % os.getcwd())
        root = tree.getroot()

        root.set('val', str(sensor.value))

        r = requests.post("%s%s/%s%s/%s%s" % (
                session['gateway'],
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS,
                sensor.identificator,
                settings.CONTENT_INSTANCES
            ),
            headers = headers,
            timeout = 5,
            data = ET.tostring(root)
        )

        sensor.registered = 1
        sensor.save()
        flash('Sensor registered!', category='success')

    else:
        flash('Sensor does not exist!', category='error')

    return redirect("/sensors/")


@app.route('/sensors/<int:sensor_id>/send_value/')
def sensor_send_value(sensor_id):
    sensor = SensorInteractor.get(sensor_id)

    if sensor:
        ET.register_namespace("m2m", "http://uri.etsi.org/m2m")

        headers = {'Authorization': 'Basic %s' % session['post-auth'], "content-type":"application/xml"}

        tree = ET.parse('%s/app/web/xml/sensor_value.xml' % os.getcwd())
        root = tree.getroot()

        root.set('val', str(sensor.value))

        r = requests.post("%s%s/%s%s/%s%s" % (
                session['gateway'],
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS,
                sensor.identificator,
                settings.CONTENT_INSTANCES
            ),
            headers = headers,
            timeout = 5,
            data = ET.tostring(root)
        )

        flash('Sensor value successfully sent!', category='success')

    else:
        flash('Sensor does not exist!', category='error')

    return redirect("/sensors/")
