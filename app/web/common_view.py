# -*- coding: utf-8 -*-
from . import app
from flask import render_template, request, session, redirect

from app.arduino.sensor import Sensor, SensorInteractor

import threading

@app.route('/')
def index():
    return redirect("/sensors/")

@app.route('/sensors/', methods=['GET'])
def get_sensors():
    sensors = SensorInteractor.get_all()
    return render_template("index.html", sensors = sensors )


@app.route('/sensors/', methods=['POST'])
def store_sensor():
    sensor = Sensor()

    for (key, value) in request.form.iteritems():
        setattr(sensor, key, value)

    sensor.save()
    return redirect("/sensors/%d" % sensor.id)


@app.route('/sensors/<int:sensor_id>/')
def get_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)
    return render_template("index.html", sensors = [sensor] if sensor else None)

@app.route('/sensors/<int:sensor_id>/register')
def register_sensor(sensor_id):
    SensorInteractor.register(sensor_id)
    return redirect("/sensors/%d/" % sensor_id)

@app.route('/sensors/<int:sensor_id>/', methods=['POST'])
def update_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)
    for (key, value) in request.form.iteritems():
        setattr(sensor, key, value)

    sensor.save()
    return render_template("index.html", sensors = [sensor] if sensor else None)


@app.route('/sensors/<int:sensor_id>/edit/')
def edit_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)
    for (key, value) in request.form.iteritems():
        setattr(sensor, key, value)

    sensor.save()
    return render_template("/sensor/add.html", sensor = sensor)


@app.route('/sensors/add/')
def add_sensor():
    return render_template("sensor/add.html")