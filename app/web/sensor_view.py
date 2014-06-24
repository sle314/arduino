# -*- coding: utf-8 -*-
from . import app
from flask import render_template, request, session, redirect, flash, abort, make_response, jsonify
from sqlalchemy.exc import IntegrityError

import os
from app.settings import local as settings
import requests

from app.arduino.gateway import GatewayInteractor
from app.arduino.sensor import Sensor, SensorInteractor, SensorMethods, SensorMethodsInteractor
from app.arduino.hardware import Pin, PinInteractor, ModuleInteractor, MethodInteractor

from app.helpers import request_helper


@app.route('/sensors/', methods=['GET'])
def get_sensors():
    sensors = SensorInteractor.get_all()
    return render_template("sensor/index.html", sensors = sensors )


@app.route('/sensors/change_view/<view>/')
def change_view_to_list(view):
    session['sensor_view'] = view
    return redirect("/sensors/")

@app.route('/sensors/', methods=['POST'])
def store_sensor():
    sensor = Sensor()

    if request.form.get('identificator') == "":
        flash('You left the identificator blank, try again!', category={ 'theme': 'error' } )
        app.logger.error("Adding sensor: Blank identificator")
        return redirect('/sensors/add/')

    if request.form.get('type'):
        sensor.type = request.form.get('type')

    sensor.identificator = request.form.get("identificator").lower().replace(" ", "_")
    sensor.pin_id = request.form.get("pin")
    sensor.module_id = request.form.get("module")

    if SensorInteractor.get_by_identificator(sensor.identificator):
        flash("Sensor with same identifier already exists!", category={ 'theme': 'error' } )
        app.logger.error("Adding sensor: Identificator already exists")
        return redirect("/sensors/add/")

    try:
        sensor.save()

        for method in sensor.module.methods:
            sm = SensorMethods()
            sm.method = method
            sensor.sensor_methods.append(sm)

        sensor.save()

        if request.form.get('is_active'):

            activate_sensor(sensor.id)

            if sensor.pin.arduino_pin == "D":
                r = request_helper.change_pin_mode(sensor.pin.arduino_pin[1:], sensor.pin.io)

                if r!= False:
                    flash("Pin %s mode successfully changed to %s!" % (sensor.pin.arduino_pin, sensor.pin.io), category={'theme' : 'success'} )
                else:
                    flash("Pin mode could not be changed!", category={'theme': 'error'})
                    app.logger.error("Adding sensor: Couldn't change pin mode - %s (%s)" % (sensor.pin.arduino_pin, sensor.pin.io))

        flash("Sensor added!", category={ 'theme': 'success' } )
        return redirect("/sensors/#%s" % sensor.identificator)

    except IntegrityError:
        flash("Sensor with same identifier already exists!", category={ 'theme': 'error' } )
        app.logger.error("Adding sensor: Identificator already exists")
        return redirect("/sensors/add/")


@app.route('/sensors/<int:sensor_id>/', methods=['POST'])
def update_sensor(sensor_id):
    identificator = request.form.get("identificator").lower().replace(" ", "_")
    old_sensor = SensorInteractor.get(sensor_id)
    old_io = old_sensor.pin.io
    sensor = SensorInteractor.get_by_identificator(identificator)

    if old_sensor:
        if sensor and sensor != old_sensor:
            flash("Sensor with same identifier already exists!", category={ 'theme': 'error' } )
            app.logger.error("Editing sensor: Identificator already exists")
            return redirect("/sensors/%d/edit/" % sensor_id)

        identificator_changed = False

        if old_sensor.identificator != identificator:
            identificator_changed= True
            old_sensor.identificator = identificator
            gateways = GatewayInteractor.get_all_device_registered()
            if gateways:
                for gateway in gateways:
                    for sensor_method in old_sensor.sensor_methods:
                        request_helper.delete_sensor(gateway.address, gateway.post_authorization, old_sensor.identificator, sensor_method.method.path)

        if request.form.get('type'):
            old_sensor.type = request.form.get('type')

        old_sensor.pin_id = request.form.get("pin")

        if old_sensor.module_id != request.form.get("module"):
            old_sensor.module_id = request.form.get("module")

            if not identificator_changed:
                gateways = GatewayInteractor.get_all_device_registered()
                if gateways:
                    for gateway in gateways:
                        for sensor_method in old_sensor.sensor_methods:
                            request_helper.delete_sensor(gateway.address, gateway.post_authorization, old_sensor.identificator, sensor_method.method.path)

            old_sensor.save()

            SensorMethodsInteractor.delete_all_for_sensor(old_sensor.id)

            for method in old_sensor.module.methods:
                sm = SensorMethods()
                sm.method = method
                old_sensor.sensor_methods.append(sm)

        old_sensor.save()

        if request.form.get('is_active'):

            activate_sensor(old_sensor.id)

            if old_sensor.pin.arduino_pin[0] == "D" and old_sensor.pin.io != old_io:
                r = request_helper.change_pin_mode(old_sensor.pin.arduino_pin[1:], old_sensor.pin.io)

                if r!= False:
                    flash("Pin %s mode successfully changed to %s!" % (old_sensor.pin.arduino_pin, old_sensor.pin.io), category={'theme' : 'success'} )
                else:
                    flash("Pin mode could not be changed!", category={'theme': 'error'})
                    app.logger.error("Editing sensor: Couldn't change pin mode - %s (%s)" % (old_sensor.pin.arduino_pin, old_sensor.pin.io))

        elif old_sensor.active:
            deactivate_sensor(old_sensor.id)

        flash("Sensor edited!", category={ 'theme': 'success' } )
        return redirect("/sensors/#%s" % old_sensor.identificator)

    flash("Sensor doesn't exist!", category={ 'theme': 'error' } )
    app.logger.error("Editing sensor: Sensor doesn't exist")
    return redirect("/sensors/")


@app.route('/sensors/<int:sensor_id>/edit/')
def edit_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)
    if sensor:
        return render_template("/sensor/add.html", sensor = sensor, modules = ModuleInteractor.get_all() )

    flash("Sensor doesn't exist!", category={ 'theme': 'error' } )
    app.logger.error("Sensor editing view: Sensor doesn't exist")
    return redirect("/sensors/")


@app.route('/sensors/add/')
def add_sensor():
    return render_template("sensor/add.html", modules = ModuleInteractor.get_all() )


@app.route('/sensors/delete/', methods=['POST'])
def delete_sensor(sensor_id=None):
    if not sensor_id:
        sensor_id = request.form.get('sensor_id')

    sensor = SensorInteractor.get(sensor_id)

    if sensor:
        if sensor.active:
            gateways = GatewayInteractor.get_all_device_registered()

            if gateways:
                deleted_all_remote = True
                for gateway in gateways:
                    for sensor_method in sensor.sensor_methods:
                        r = request_helper.delete_sensor(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path)
                        if r == False:
                            flash("Sensor method %s was not deleted on gateway %s!" % (sensor_method.method.path, gateway.address), category={ 'theme': 'warning' } )
                            deleted_all_remote = False

                    if deleted_all_remote:
                        if SensorInteractor.delete(sensor_id):
                            flash("Sensor deleted from gateway %s!" % gateway.address, category={ 'theme': 'success' } )
                    else:
                        flash("Sensor could not be deleted!", category={ 'theme': 'error' })
                        app.logger.error("Deleting sensor: Couldn't delete sensor from db because not all sensor methods could be deleted from GW")
                        return redirect("/sensors/#%s" % sensor.identificator)

                    request_helper.send_descriptor(gateway.address, gateway.post_authorization)
            else:
                flash("No gateways with registered device", category={ 'theme': 'warning' } )

        else:
            if SensorInteractor.delete(sensor_id):
                flash("Sensor deleted!", category={ 'theme': 'success' } )
            else:
                flash("Sensor could not be deleted!", category={ 'theme': 'error' } )
                app.logger.error("Deleting sensor: Could not delete sensor from db")
                return redirect("/sensors/#%s" % sensor.identificator)

    else:
        flash('Sensor does not exist!', category={ 'theme': 'error' } )
        app.logger.error("Deleting sensor: Sensor does not exist")
    return redirect("/sensors/")

@app.route('/sensors/<int:sensor_id>/send_values/')
def sensor_send_value(sensor_id):
    sensor = SensorInteractor.get(sensor_id)

    if sensor:
        if sensor.active:
            gateways = GatewayInteractor.get_all_device_registered()

            if gateways:
                for gateway in gateways:
                    for sensor_method in sensor.sensor_methods:
                        if sensor_method.method.type == "write" and sensor_method.value:
                            r = request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path, sensor_method.value)
                        elif sensor_method.method.type == "read":
                            sensor_method.value = request_helper.get_sensor_value(sensor, sensor_method.method.path)
                            sensor_method.save()
                            r = request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path, sensor_method.value)
                    if r != False:
                        flash('Sensor method values successfully sent to gateway %s!' % gateway.address, category={ 'theme' : 'success' } )
            else:
                flash("No gateways with registered device!", category={ 'theme': 'warning' } )

            return redirect("/sensors/#%s" % sensor.identificator)
        else:
            flash('Sensor is not active!', category={ 'theme': 'warning' } )
            return redirect("/sensors/#%s" % sensor.identificator)

    flash('Sensor does not exist!', category={ 'theme': 'error' } )
    app.logger.error("Sending sensor values: Sensor does not exist")
    return redirect("/sensors/")

@app.route('/retargeting1/sensors/<identificator>/<method_path>', methods = ['POST'])
@app.route('/retargeting1/sensors/<identificator>/<method_path>/<value>', methods = ['POST'])
def retargeting_sensor_toggle(identificator, method_path, value=None):
    if request.remote_addr in [gateway.address.split(":")[1][2:] for gateway in GatewayInteractor.get_all_device_registered()]:
        sensor = SensorInteractor.get_by_identificator(identificator)
        if sensor and sensor.active:
            method = MethodInteractor.get_by_path(method_path, sensor.module_id)
            if method:
                if method.type != "read":
                    sensor_method = SensorMethodsInteractor.get(sensor.id, method.id)
                    if sensor_method:
                        if sensor.pin.io == "output":
                            path = "/%s/%s/%s/%s" % (sensor.module.hardware.path, sensor.module.path, method_path, sensor.pin.pin)
                            if value:
                                path += "/%s" % value
                            r = request_helper.call_arduino_path( path )
                            if r != False:
                                if r.status_code == 200:
                                    if r.text:
                                        sensor_method.value = r.text
                                        sensor_method.save()
                                        for gateway in GatewayInteractor.get_all_device_registered():
                                            request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path, sensor_method.value)
                                        app.logger.info("Retargeting call: %s - %s (%s)" % (identificator, method_path, sensor_method.value))
                                return make_response((r.text, r.status_code))
                            app.logger.error("Retargeting call: Can't reach sensor - %s" % (sensor.identificator, ))
                            return make_response(("400: The sensor can't be reached!", 400))
                        app.logger.error("Retargeting call: Called method for an INPUT sensor - %s" % (sensor.identificator))
                        return make_response(("400: You are calling a method for an INPUT sensor!", 400))
                    app.logger.error("Retargeting call: Invalid method for sensor - %s (%s)" % (sensor.identificator, method_path))
                    return make_response(("400: Invalid method for sensor!", 400))
                app.logger.error("Retargeting call: Called read method - %s (%s)" % (sensor.identificator, method_path))
                return make_response(("400: You are calling a read method!", 400))
            app.logger.error("Retargeting call: Invalid method for sensor - %s (%s)" % (sensor.identificator, method_path))
            return make_response(("400: Invalid method for sensor!", 400))
        app.logger.error("Retargeting call: Sensor doesn't exist - %s" % (identificator, ))
        return make_response(("400: Non existant sensor!", 400))
    app.logger.error("Retargeting call: Request didn't come from registered GW - %s" % (request.remote_addr, ))
    return make_response(("400: You are not allowed to access this device!", 400))


@app.route('/sensors/<int:sensor_id>/activate/')
def activate_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)
    if sensor:
        sensors = SensorInteractor.get_active_for_pin(sensor.pin.arduino_pin)
        old_io = ""
        if sensors:
            for sensor_on_pin in sensors:
                deactivate_sensor(sensor_on_pin.id, False)
                old_io = sensor_on_pin.pin.io

        sensor.active = True
        sensor.save()

        if sensor.pin.io != old_io:
            r = request_helper.change_pin_mode(sensor.pin.arduino_pin, sensor.pin.io)
            if r != False:
                flash("Pin %s mode successfully changed to %s!" % (sensor.pin.arduino_pin, sensor.pin.io), category={'theme' : 'success'} )
            else:
                flash("Pin mode could not be changed!", category={'theme': 'error'})
                app.logger.error("Activating sensor: Couldn't change pin mode - %s (%s)" % (sensor.pin.arduino_pin, sensor.pin.io))

        for sensor_method in sensor.sensor_methods:
            if sensor_method.method.type in ["read"]:
                r = request_helper.get_sensor_value(sensor, sensor_method.method.path)
                if r != False:
                    sensor_method.value = r
                    sensor_method.save()

        gateways = GatewayInteractor.get_all_device_registered()

        if gateways:
            for gateway in gateways:
                r = request_helper.send_descriptor(gateway.address, gateway.post_authorization)
                if r != False:
                    for sensor_method in sensor.sensor_methods:
                        r = request_helper.init_sensor(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path)
                        if r != False and sensor_method.method.type in ["read", "write"] and sensor_method.value:
                            r = request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path, sensor_method.value)
                    flash('Sensor successfully added to gateway %s!' % gateway.address, category={ 'theme': 'success' } )
            flash("Sensor activated!", category={ 'theme': 'success' } )
        else:
            flash("No gateways with registered device", category={ 'theme': 'warning' } )

        return redirect("/sensors/#%s" % sensor.identificator)

    flash("Sensor does not exist!", category={ 'theme': 'error' } )
    app.logger.error("Activating sensor: Sensor does not exist")
    return redirect("/sensors/")



@app.route('/sensors/<int:sensor_id>/deactivate/')
def deactivate_sensor(sensor_id, descriptor=True):
    sensor = SensorInteractor.get(sensor_id)
    if sensor:
        sensor.active = False
        sensor.save()
        gateways = GatewayInteractor.get_all_device_registered()

        if gateways:
            for gateway in gateways:
                if descriptor:
                    r = request_helper.send_descriptor(gateway.address, gateway.post_authorization)
                for sensor_method in sensor.sensor_methods:
                    r = request_helper.delete_sensor(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path)
                if r != False:
                    flash('Sensor successfully removed from gateway %s!' % gateway.address, category={ 'theme': 'success' } )
        else:
            flash("No gateways with registered device", category={ 'theme': 'warning' } )
        flash("Sensor deactivated!", category={ 'theme': 'success' } )
        return redirect("/sensors/#%s" % sensor.identificator)

    flash("Sensor does not exist!", category={ 'theme': 'error' } )
    app.logger.error("Activating sensor: Sensor does not exist")
    return redirect("/sensors/")


@app.route('/sensors/<int:sensor_id>/methods/<int:method_id>/invoke/', methods=['POST'])
def invoke_sensor_method(sensor_id, method_id):
    path = request.form.get("path")
    r = request_helper.call_arduino_path(path)

    app.logger.info("Invoking method %d for sensor %d: %s (status %d)" % (method_id, sensor_id, r.text, r.status_code))

    if r != False:
        if r.status_code == 200:
            values = []
            sensor_method = SensorMethodsInteractor.get(sensor_id, method_id)
            if r.text != "":
                sensor_method.value = r.text
                sensor_method.save()
                if sensor_method.method.type in ["write", "call"]:
                    sensor = SensorInteractor.get(sensor_id)
                    if sensor:
                        for sensor_method in sensor.sensor_methods:
                            if sensor_method.method.type == "read":
                                rq = request_helper.call_arduino_path("/%s/%s/%s/%s" % (sensor.module.hardware.path, sensor.module.path, sensor_method.method.path, sensor.pin.pin))
                                if rq != False:
                                    sensor_method.value = rq.text
                                    sensor_method.save()
                                values.append({"path":sensor_method.method.path, "value" : sensor_method.value})

                return jsonify({ "value" : r.text, "values": values })
        elif r.status_code == 500:
            app.logger.error("Invoking method: Couldn't connect to YunServer - sensor %s (method %s) - path %s" % (sensor_id, method_id, path))
            return jsonify({ "value" : 'error', 'error' : 'The server is not available.' })

    app.logger.error("Invoking method: Something went wrong - sensor %s (method %s) - path %s" % (sensor_id, method_id, path))
    return jsonify({ "value" : 'error', 'error' : 'Something went wrong while contacting the server.' })


@app.route('/sensors/check_identificator/', methods=['POST'])
def check_identificator():
    identificator = request.form.get("identificator")
    sensor = SensorInteractor.get_by_identificator(identificator)
    if sensor:
        return jsonify({ "exists" : True })
    return jsonify({ "exists" : False })