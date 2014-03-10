from app.arduino import app
from flask import render_template

from app.models.sensor import Sensor

@app.route('/')
def index():
    sensor = Sensor(2, "Temperature", 23.4, "Celsius")
    print sensor
    return render_template("index.html", sensor = sensor)

@app.route('/sensor/<int:sensor_id>/')
def get_sensor(sensor_id):
    sensor = Sensor()
    sensor.get(sensor_id)
    return render_template("index.html", sensor = sensor)