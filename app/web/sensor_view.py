# -*- coding: utf-8 -*-
from . import app
from flask import render_template, request, session, redirect, flash, abort, make_response, jsonify
from sqlalchemy.exc import IntegrityError

import os
from app.settings import local as settings
import requests

from app.arduino.gateway import GatewayInteractor
from app.arduino.sensor import Sensor, SensorInteractor
from app.arduino.hardware import Pin, PinInteractor, ModuleInteractor, MethodInteractor

from app.helpers import request_helper


@app.route('/sensors/', methods=['GET'])
def get_sensors():
    sensors = SensorInteractor.get_all()
    return render_template("sensor/index.html", sensors = sensors )


@app.route('/sensors/', methods=['POST'])
def store_sensor():
    sensor = Sensor()

    if request.form.get('identificator') == "":
        flash('You left the identificator blank, try again!', category={ 'theme': 'error' } )
        return redirect('/sensors/add/')

    if request.form.get('type'):
        sensor.type = request.form.get('type')

    sensor.identificator = request.form.get("identificator").lower().replace(" ", "_")
    sensor.pin_id = request.form.get("pin")
    sensor.module_id = request.form.get("module")

    if SensorInteractor.get_by_identificator(sensor.identificator):
        flash("Sensor with same identifier already exists!", category={ 'theme': 'error' } )
        return redirect("sensors/add/")

    try:
        sensor.save()

        if request.form.get('is_active'):

            activate_sensor(sensor.id)

            if sensor.pin.pin == "D":
                r = request_helper.change_pin_mode(sensor.pin.pin[1:], sensor.pin.io)

                if r!= False:
                    flash("Pin %s mode successfully changed to %s!" % (sensor.pin.arduino_pin, sensor.pin.io), category={'theme' : 'success'} )
                else:
                    flash("Pin mode could not be changed!", category={'theme': 'error'})

        flash("Sensor added!", category={ 'theme': 'success' } )
        return redirect("/sensors/#%s" % sensor.identificator)
    except IntegrityError:
        flash("Sensor with same identifier already exists!", category={ 'theme': 'error' } )
        return redirect("sensor/add/")


@app.route('/sensors/<int:sensor_id>/', methods=['POST'])
def update_sensor(sensor_id):
    identificator_changed = False
    identificator = request.form.get("identificator").lower().replace(" ", "_")
    old_sensor = SensorInteractor.get(sensor_id)
    old_io = old_sensor.pin.io
    sensor = SensorInteractor.get_by_identificator(identificator)

    if old_sensor:
        if sensor and sensor != old_sensor:
            flash("Sensor with same identifier already exists!", category={ 'theme': 'warning' } )
            return redirect("/sensors/%d/edit/" % sensor_id)

        if old_sensor.identificator != identificator:
            gateways = GatewayInteractor.get_all_device_registered()
            if gateways:
                for gateway in gateways:
                    request_helper.delete_sensor(gateway.address, gateway.post_authorization, old_sensor.identificator)

        if request.form.get('type'):
            old_sensor.type = request.form.get('type')

        old_sensor.identificator = identificator
        old_sensor.pin_id = request.form.get("pin")
        old_sensor.module_id = request.form.get("module")

        old_sensor.save()

        if request.form.get('is_active'):

            activate_sensor(sensor_id)

            if old_sensor.pin.pin[0] == "D" and old_sensor.pin.io != old_io:
                r = request_helper.change_pin_mode(old_sensor.pin.pin[1:], old_sensor.pin.io)

                if r!= False:
                    flash("Pin %s mode successfully changed to %s!" % (old_sensor.pin.pin, old_sensor.pin.io), category={'theme' : 'success'} )
                else:
                    flash("Pin mode could not be changed!", category={'theme': 'error'})
        else:
            deactivate_sensor(sensor_id)

        flash("Sensor edited!", category={ 'theme': 'success' } )
        return redirect("/sensors/#%s" % old_sensor.identificator)
    else:
        flash("Sensor doesn't exist!", category={ 'theme': 'error' } )
        return redirect("/sensors/")


@app.route('/sensors/<int:sensor_id>/edit/')
def edit_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)
    return render_template("/sensor/add.html", sensor = sensor, modules = ModuleInteractor.get_all() )


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
                for gateway in gateways:
                    for method in sensor.module.methods:

                        r = request_helper.delete_sensor(gateway.address, gateway.post_authorization, sensor.identificator, method.path)

                        if r != False:
                            if r.status_code == 204:
                                if SensorInteractor.delete(sensor_id):
                                    request_helper.send_descriptor(gateway.address, gateway.post_authorization)
                                    flash("Sensor deleted from gateway %s!" % gateway.address, category={ 'theme': 'success' } )
                                else:
                                    request_helper.send_descriptor(gateway.address, gateway.post_authorization)
                                    flash("Sensor was deleted on gateway %s but not locally!" % gateway.address, category={ 'theme': 'error' } )
                                    return redirect("/sensors/#%s" % sensor.identificator)
                            else:
                                flash("Sensor could not be deleted on gateway %s!" % gateway.address, category={ 'theme': 'error' } )
                                return redirect("/sensors/#%s" % sensor.identificator)
            else:
                flash("No gateways with registered device", category={ 'theme': 'warning' } )

        else:
            if SensorInteractor.delete(sensor_id):
                flash("Sensor deleted!", category={ 'theme': 'success' } )
            else:
                flash("Sensor could not be deleted!", category={ 'theme': 'error' } )
                return redirect("/sensors/#%s" % sensor.identificator)
    else:
        flash('Sensor does not exist!', category={ 'theme': 'error' } )

    return redirect("/sensors/")

@app.route('/sensors/<int:sensor_id>/send_value/')
def sensor_send_value(sensor_id):
    sensor = SensorInteractor.get(sensor_id)

    if sensor and sensor.active:
        r = request_helper.get_from_pin(sensor.ad, sensor.pin[1:])
        if r != False:
            val = r.text
            if sensor.pin[0] == "A":
                value = sensor.min_value + ((int(val)/1024.0)*(sensor.max_value-sensor.min_value))
                SensorInteractor.set_value(sensor_id, "%0.1f" % value)
            else:
                if val != sensor.value:
                    SensorInteractor.set_value(sensor_id, "%s" % val)

            gateways = GatewayInteractor.get_all_device_registered()

            if gateways:
                for gateway in gateways:
                    for method in sensor.module.methods:
                        if method.type == "read":
                            r = request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, method.path, method.value)
                    if r != False:
                        flash('Sensor value successfully sent to gateway %s!' % gateway.address, category={ 'theme' : 'success' } )
            else:
                flash("No gateways with registered device!", category={ 'theme': 'warning' } )

            return redirect("/sensors/#%d" % sensor_id)
        else:
            flash("Insignificant change of sensor value for the set threshold! Value wasn't sent!", category={ 'theme': 'warning' } )
    else:
        flash('Sensor does not exist!', category={ 'theme': 'error' } )

    return redirect("/sensors/")


@app.route('/retargeting1/sensors/<identificator>/<method_path>/', methods = ['POST'])
def retargeting_sensor_toggle(identificator, method_path):
    sensor = SensorInteractor.get_by_identificator(identificator)
    method = MethodInteractor.get_by_path(method_path, sensor.module_id)

    if sensor and sensor.active:
        if sensor.pin.io == "output":
            r = request_helper.call_arduino_path("/%s/%s/%s/%s" % (sensor.module.hardware.path, sensor.module.path, method_path, sensor.pin.pin) )
            if r != False:
                if r.status_code == 200:
                    if r.text:
                        method.value = r.text
                        method.save()
                        for gateway in GatewayInteractor.get_all_device_registered():
                            request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, method.path, method.value)
                return make_response((r.text, r.status_code))
    return abort(400)



@app.route('/sensors/<int:sensor_id>/toggle/')
def sensor_toggle(sensor_id):
    sensor = SensorInteractor.get(sensor_id)

    if sensor and sensor.active:
        if sensor.io == "output":
            r = request_helper.toggle_sensor(sensor.ad, sensor.pin[1:])
            if r != False:
                if r.status_code == 200:
                    if r.text:
                        sensor.value = r.text
                        sensor.save()
                        flash("Sensor toggled!", category={ 'theme': 'success' } )
                        for gateway in GatewayInteractor.get_all_device_registered():
                            request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor.value)

                    else:
                        flash("Could not toggle device!", category={ "theme" : "error" })
                else:
                    flash("Could not toggle device!", category={ "theme" : "error" })
        return redirect("/sensors/#%d" % sensor_id)

    flash('Sensor does not exist!', category={ 'theme': 'error' } )
    return redirect("/sensors/")


@app.route('/sensors/<int:sensor_id>/activate/')
def activate_sensor(sensor_id):
    sensor = SensorInteractor.get(sensor_id)
    if sensor:
        sensors = SensorInteractor.get_active_for_pin(sensor.pin.arduino_pin)
        if sensors:
            for sensor_on_pin in sensors:
                deactivate_sensor(sensor_on_pin.id, False)

        sensor.active = True
        sensor.save()
        gateways = GatewayInteractor.get_all_device_registered()

        if gateways:
            for gateway in gateways:
                r = request_helper.send_descriptor(gateway.address, gateway.post_authorization)
                if r != False:
                    for method in sensor.module.methods:
                        r = request_helper.init_sensor(gateway.address, gateway.post_authorization, sensor.identificator, method.path)
                        if method.type == "read":
                            r = request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, method.path, method.value)
                    flash('Sensor successfully added to gateway %s!' % gateway.address, category={ 'theme': 'success' } )
        else:
            flash("No gateways with registered device", category={ 'theme': 'warning' } )

        flash("Sensor activated!", category={ 'theme': 'success' } )
        return redirect("/sensors/#%s" % sensor.identificator)

    flash("Sensor does not exist!", category={ 'theme': 'error' } )
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
                for method in sensor.module.methods:
                    r = request_helper.delete_sensor(gateway.address, gateway.post_authorization, sensor.identificator, method.path)
                if r != False:
                    flash('Sensor successfully removed from gateway %s!' % gateway.address, category={ 'theme': 'success' } )
        else:
            flash("No gateways with registered device", category={ 'theme': 'warning' } )
        flash("Sensor deactivated!", category={ 'theme': 'success' } )
        return redirect("/sensors/#%s" % sensor.identificator)
    else:
        flash("Sensor does not exist!", category={ 'theme': 'error' } )
    return redirect("/sensors/")


@app.route('/sensors/write/', methods=['POST'])
def write_to_sensor():
    sensor = SensorInteractor.get(int(request.form["sensor_id"]))
    sensor.value = request.form["value"]
    sensor.save()
    for gateway in GatewayInteractor.get_all_device_registered():
        for method in sensor.module.methods:
            if method.type == "read":
                request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, method.path, method.value)
    request_helper.write_to_pin(sensor.ad, sensor.pin[1:], sensor.value)
    return redirect("/sensors/#%s" % sensor.id)


@app.route('/modules/<int:module_id>/pins/', methods=['GET'])
def get_pins_for_module(module_id):
    pins = ModuleInteractor.get_pins(module_id)
    return render_template("/common/pin_select.html", pins = pins)


@app.route('/modules/<int:module_id>/methods/<int:method_id>/invoke/', methods=['POST'])
def invoke_sensor_method(module_id, method_id):
    path = request.form.get("path")
    r = request_helper.call_arduino_path(path)

    method = MethodInteractor.get(method_id)
    method.value = r.text
    method.save()

    return jsonify({ "value" : r.text })
