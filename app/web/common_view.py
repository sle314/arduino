# -*- coding: utf-8 -*-
from app.settings import local as settings

from app.web import app

from app.helpers import request_helper

from flask import render_template, request, make_response
from app.arduino.gateway import GatewayInteractor
from app.arduino.sensor import SensorInteractor

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
    if len(sensors) > 0:
        for sensor in sensors:
            if sensor.identificator != identificator:
                sensor_dict[str(sensor.id)] = sensor.identificator
    return jsonify(sensor_dict)


@app.route('/cron/')
def cron():
    for gateway in GatewayInteractor.get_all_device_registered():
        for sensor in SensorInteractor.get_all_active():
            for sensor_method in sensor.sensor_methods:
                if sensor_method.method.type == "read":
                    sensor_method.value = request_helper.get_sensor_value(sensor, sensor_method.method.path)
                    sensor_method.save()
                    request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path, sensor_method.value)
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
            r = request_helper.delete_device(gateway.address, gateway.post_authorization)
            print "Delete dev: %d" % r.status_code
            r = request_helper.init_device(gateway.address, gateway.post_authorization)
            print "Init dev: %d" % r.status_code
            r = request_helper.init_descriptor(gateway.address, gateway.post_authorization)
            print "Init descriptor: %d" % r.status_code
            r = request_helper.send_descriptor(gateway.address, gateway.post_authorization)
            print "Descriptor: %d" % r.status_code
            for sensor in SensorInteractor.get_all_active():
                for sensor_method in sensor.sensor_methods:
                    r = request_helper.delete_sensor(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path)
                    print "Delete sensor method %s: %d" % (sensor_method.method.path, r.status_code)
                    r = request_helper.init_sensor(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path)
                    print "Init sensor method %s: %d" % (sensor_method.method.path, r.status_code)
                    if method.type in ["read", "write"]:
                        r = request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path, sensor_method.value)
                        print "Send method value %s: %d" % (sensor_method.method.path, r.status_code)
    return make_response()
