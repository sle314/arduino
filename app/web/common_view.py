# -*- coding: utf-8 -*-
import sys
from app.settings import local as settings

from app.web import app

from app.helpers import request_helper

from flask import render_template, request, make_response, abort
from app.arduino.gateway import GatewayInteractor
from app.arduino.sensor import SensorInteractor

from flask import json, jsonify

@app.before_request
def before_request():
    if request.endpoint != "static":
        if not ".".join(request.remote_addr.split(".")[0:3]) == "161.53.19" and\
        not ".".join(request.remote_addr.split(".")[0:3]) == "192.168.1" and\
        not request.remote_addr == "127.0.0.1" and\
        not request.remote_addr in [gateway.address.split(":")[1][2:] for gateway in GatewayInteractor.get_all_device_registered()]:
            app.logger.error( "%s" % "-"*20 )
            app.logger.error( "REQUEST FOR ACCESS FROM NON-ALLOWED ADDRESS - %s" % (request.remote_addr, ) )
            app.logger.error( "%s" % "-"*20 )
            return abort(400)


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
    app.logger.info("----START cron START----")
    try:
        for gateway in GatewayInteractor.get_all_device_registered():
            for sensor in SensorInteractor.get_all_active():
                for sensor_method in sensor.sensor_methods:
                    if sensor_method.method.type in ["read", "write"]:
                        if sensor_method.method.type == "read":
                            r = request_helper.get_sensor_value(sensor, sensor_method.method.path)
                            if r != False:
                                sensor_method.value = r
                                sensor_method.save()
                                if sensor_method.value:
                                    r = request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path, sensor_method.value)
                                    if r != False:
                                        log = "%s - %s %s %s - %s (%s)" % ( gateway.address, sensor.module.hardware.name, sensor.module.name, sensor.identificator, sensor_method.method.path, sensor_method.value )
                                        app.logger.info(log)
    except:
        app.logger.error( "%s" % sys.exc_info()[0] )
    app.logger.info("----END cron END----")
    return make_response()


@app.route('/ip_cron/')
def ip_cron():
    import json
    from app.arduino.common import PublicIPInteractor
    from urllib2 import urlopen

    ip = PublicIPInteractor.get()
    currentIP = json.load(urlopen('http://httpbin.org/ip'))['origin'].rstrip()

    app.logger.info("---- START IP cron START----")
    app.logger.info("IP ADDRESS - %s" % currentIP)

    if (not ip.address or ip.address != currentIP):
        try:
            for gateway in GatewayInteractor.get_all_device_registered():
                r = request_helper.delete_device(gateway.address, gateway.post_authorization)
                if r != False:
                    app.logger.info("Delete dev: %d" % r.status_code)
                    ip.address = currentIP
                    ip.save()
                    r = request_helper.init_device(gateway.address, gateway.post_authorization)
                    if r != False:
                        app.logger.info("Init dev: %d" % r.status_code)
                        r = request_helper.init_descriptor(gateway.address, gateway.post_authorization)
                        if r != False:
                            app.logger.info("Init descriptor: %d" % r.status_code)
                            r = request_helper.send_descriptor(gateway.address, gateway.post_authorization)
                            if r != False:
                                app.logger.info("Descriptor: %d" % r.status_code)
                                for sensor in SensorInteractor.get_all_active():
                                    for sensor_method in sensor.sensor_methods:
                                        r = request_helper.delete_sensor(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path)
                                        if r != False:
                                            app.logger.info("Delete sensor method %s: %d" % (sensor_method.method.path, r.status_code))
                                            r = request_helper.init_sensor(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path)
                                            if r != False:
                                                app.logger.info("Init sensor method %s: %d" % (sensor_method.method.path, r.status_code))
                                                if sensor_method.method.type in ["read", "write"]:
                                                    r = request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path, sensor_method.value)
                                                    if r != False:
                                                        app.logger.info("Send method value %s: %d" % (sensor_method.method.path, r.status_code))
                                                        log = "%s - %s %s %s - %s (%s)" % ( gateway.address, sensor.module.hardware.name, sensor.module.name, sensor.identificator, sensor_method.method.path, sensor_method.value )
                                                        app.logger.info(log)
                            else:
                                ip.address = ""
                                ip.save()
                        else:
                            ip.address = ""
                            ip.save()
                    else:
                        ip.address = ""
                        ip.save()
        except:
            app.logger.error( "%s" % sys.exc_info()[0] )
            ip.address = ""
            ip.save()
    else:
        app.logger.warning("address wasn't changed")
    app.logger.info("----END IP cron END----")
    return make_response()
