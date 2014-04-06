# -*- coding: utf-8 -*-
from app.settings import local as settings

from app.web import app

from flask import render_template, request, make_response
from app.arduino.gateway import GatewayInteractor
from app.arduino.sensor import SensorInteractor

from app.helpers.request_helper import get_sensor_values, send_sensor_value

from flask import json, jsonify

@app.before_request
def before_request():
    if request.endpoint != "static":
        pass


@app.route('/')
def index():
    return render_template("gateway/index.html", settings=settings, gateways=GatewayInteractor.get_all())


@app.route('/check_pin/<identificator>/<pin>/')
def check_pin(identificator, pin):
    sensors = SensorInteractor.get_active_for_pin(pin)
    sensor_dict = {}
    if sensors:
        for sensor in sensors:
            if sensor.identificator != identificator:
                sensor_dict[str(sensor.id)] = sensor.identificator
    return jsonify(sensor_dict)


@app.route('/cron/')
def cron():
    values = get_sensor_values()

    for gateway in GatewayInteractor.get_all_device_registered():
        for sensor in SensorInteractor.get_all_active():
            new_value = values[sensor.pin]
            check = True
            if sensor.pin[0] == "A":
                old_value = float(sensor.value)

                value = sensor.min_value + ((int(new_value)/1024.0)*(sensor.max_value-sensor.min_value))
                sensor.value = "%0.1f" % value
                check = abs( old_value - float(sensor.value) ) < sensor.threshold
            else:
                if new_value != sensor.value:
                    check = False
                    sensor.value = new_value

            sensor.save()
            if ( not check ):
                send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor.value)
    return make_response()


@app.route('/ip_cron/')
def ip_cron():
    import json
    from app.arduino.common import PublicIPInteractor
    from urllib2 import urlopen

    ip = PublicIPInteractor.get()
    currentIP = json.load(urlopen('http://httpbin.org/ip'))['origin'].rstrip()

    if (not ip.address or ip.address != currentIP):
        ip.address = currentIP
        ip.save()
        for gateway in GatewayInteractor.get_all_device_registered():
            request_helper.delete_device(gateway.address, gateway.post_authorization)
            request_helper.init_device(gateway.address, gateway.post_authorization)
            request_helper.init_descriptor(gateway.address, gateway.post_authorization)
            request_helper.send_descriptor(gateway.address, gateway.post_authorization)
            for sensor in SensorInteractor.get_all_active():
                request_helper.init_sensor(gateway.address, gateway.post_authorization, sensor.identificator)
    return make_response()
