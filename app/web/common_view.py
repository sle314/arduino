# -*- coding: utf-8 -*-
from . import app
from flask import render_template, request, session, redirect

from app.models.sensor import Sensor

@app.route('/')
def index():
    return render_template("index.html" )


@app.route('/sensor/', methods=['POST'])
def store_sensor():
    from random import randrange
    sensor_id = randrange(0,9)
    sensor = Sensor(sensor_id)

    for (key, value) in request.form.iteritems():
        setattr(sensor, key, value)
    session[str(sensor_id)] = sensor.to_json()
    return redirect("/sensor/%d" % sensor.id)
    # return redirect("/")


@app.route('/sensor/<int:sensor_id>/')
def get_sensor(sensor_id):
    print session
    if str(sensor_id) in session:
        print session
        return render_template("index.html", sensor = session[str(sensor_id)])
    else:
        return redirect("/")