# -*- coding: utf-8 -*-
from . import app
from flask import render_template, request, redirect, flash
from sqlalchemy.exc import IntegrityError

from app.arduino.sensor import Sensor, SensorInteractor


@app.route('/sensors/', methods=['GET'])
def get_sensors():
    sensors = SensorInteractor.get_all()
    return render_template("sensor/index.html", sensors = sensors )


@app.route('/sensors/', methods=['POST'])
def store_sensor():
    sensor = Sensor()

    for (key, value) in request.form.iteritems():
        setattr(sensor, key, value.lower().replace(" ", "_") if key=="identificator" else value.replace(" ", "_"))
    try:
        sensor.save()
    except IntegrityError:
        flash("Sensor with same identifier already exists!")
        return render_template("sensor/add.html", sensor=sensor)

    flash("Sensor added!")
    return redirect("/sensors/%d/" % sensor.id)


@app.route('/sensors/<int:sensor_id>/')
def get_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)
    return render_template("sensor/index.html", sensors = [sensor] if sensor else None)


@app.route('/sensors/<int:sensor_id>/', methods=['POST'])
def update_sensor(sensor_id):
    sensor = SensorInteractor.get_by_identificator(request.form.get("identificator").lower().replace(" ", "_"))
    if sensor and sensor != SensorInteractor.get(sensor_id):
        flash("Sensor with same identifier already exists!")
        return redirect("/sensors/%d/edit/" % sensor_id)

    sensor = SensorInteractor.get(sensor_id)
    for (key, value) in request.form.iteritems():
        setattr(sensor, key, value.lower().replace(" ", "_") if key=="identificator" else value.replace(" ", "_"))

    sensor.save()

    flash("Sensor edited!")
    return render_template("sensor/index.html", sensors = [sensor] if sensor else None)


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
    if SensorInteractor.delete(sensor_id):
        flash("Sensor deleted!")
    else:
        flash("Could not delete sensor!")
    return redirect("/sensors/")