# -*- coding: utf-8 -*-
from . import app
from app.settings import local as settings
import os

from flask import render_template, request, session, redirect, flash, json
from requests.exceptions import ConnectionError, Timeout
from app.arduino.sensor import SensorInteractor
from app.arduino.gateway import Gateway, GatewayInteractor
from app.helpers import request_helper

import requests
import re

@app.route('/gateway/', methods=['POST'])
def gateway():

    gateway = Gateway()

    address = request.form.get("address")
    address = address if "http://" in address else "http://%s" % address

    if GatewayInteractor.check_address(address):
        flash("Gateway wasn't saved beacuse it already exists for this device! If you need to change the authorization, edit the existing one!", category={'theme':'warning', 'life': 6000})
        return redirect("/")

    from app.helpers.base64_helper import b64encode_quote
    authorization = b64encode_quote(request.form.get("authorization"))

    r = request_helper.check_gateway(address, authorization)

    if r != False:
        if r.status_code == 200:
            if r.text:
                m = re.findall(r'<m2m:holderRef>(.*?)</m2m:holderRef>', r.text)
                gateway.post_authorization = b64encode_quote(m[1])
                gateway.name = request.form.get("name") if request.form.get("name") else m[1].split("//")[1].split(".")[0]
                gateway.address = address
                gateway.authorization = authorization
                gateway.active = True

                try:
                    gateway.save()
                except:
                    flash("Gateway wasn't saved beacuse it already exists for this device! If you need to change the authorization, edit the existing one!", category={'theme':'warning', 'life': 6000})
                    return redirect("/")

                r = request_helper.check_device(address, authorization)

                if r != False:
                    if r.status_code == 200:
                        flash("Device is already registered on gateway!", category={ 'theme': 'success' } )
                        gateway.device_registered = True
                        gateway.save()

                        # remove_device_from_gateway(gateway.id)
                        # register_device_on_gateway(gateway.id)

                    elif r.status_code == 404:
                        flash("Device is not registered.", category={ 'theme': 'warning' } )
            else:
                flash('Response was not a valid accessRights XML!', category={ 'theme': 'error' } )
                app.logger.error("Adding gateway: Invalid accessRights XML")

        elif r.status_code == 400 or r.status_code == 404:
            flash("Wrong authorization URI! Gateway wasn't added!", category={ 'theme': 'error' } )
            app.logger.error("Adding gateway: Wrong authorization URI")

    return redirect('/')


@app.route('/gateway/<int:gateway_id>/register_device/')
def register_device_on_gateway(gateway_id):
    gateway = GatewayInteractor.get(gateway_id)
    if gateway:
        r = request_helper.init_device(gateway.address, gateway.post_authorization)

        if r != False:
            if r.status_code == 201 or r.status_code == 409:
                r = request_helper.init_descriptor(gateway.address, gateway.post_authorization)
                if r != False:
                    r = request_helper.send_descriptor(gateway.address, gateway.post_authorization)
                    if r != False:
                        sensors = SensorInteractor.get_all_active()
                        if sensors:
                            for sensor in sensors:
                                if sensor.active:
                                    sensor.save()
                                    for sensor_method in sensor.sensor_methods:
                                        r = request_helper.init_sensor(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path)
                                        if r != False and sensor_method.method.type in ["read", "write"] and sensor_method.value:
                                            request_helper.send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor_method.method.path, sensor_method.value)

                        flash('Device successfully registered!', category={ 'theme': 'success' } )
                        gateway.device_registered = True
                        gateway.save()

            elif r.status_code == 400 or r.status_code == 401:
                flash('Wrong authorization for registration!', category={ 'theme': 'error' } )
                app.logger.error("Registering device: Wrong authorization")

            else:
                flash('Something went wrong!', category={ 'theme': 'error' } )
                app.logger.error("Registering device: Unknown error during device initialization")
    else:
        flash("Gateway does not exist!", category={ 'theme': 'error' } )
        app.logger.error("Registering device: Gateway doesn't exist")

    return redirect("/")


@app.route('/gateway/<int:gateway_id>/unregister_device/')
def remove_device_from_gateway(gateway_id):

    gateway = GatewayInteractor.get(gateway_id)
    if gateway:

        r = request_helper.delete_device(gateway.address, gateway.post_authorization)

        if r != False:
            if r.status_code == 204:
                flash('Device successfully removed from gateway!', category={ 'theme': 'success' } )
                gateway.device_registered = False
                gateway.save()
            elif r.status_code == 404:
                flash('Device is already removed!', category={ 'theme': 'warning' } )
                gateway.device_registered = False
                gateway.save()
            else:
                flash('Something went wrong!', category={ 'theme': 'error' } )
                app.logger.error("Unregistering device: Unknown error during device deletion")
    else:
        flash("Gateway does not exist!", category={ 'theme': 'error' } )
        app.logger.error("Unregistering device: Gateway doesn't exist")

    return redirect('/')


@app.route('/gateway/delete/', methods=['POST'])
def remove_gateway():
    gateway_id = request.form.get('gateway_id')
    remove_device_from_gateway(gateway_id)
    if GatewayInteractor.delete(gateway_id):
        flash("Gateway successfully removed!", category={ 'theme': 'success' } )
    else:
        flash("Could not remove gateway!", category={ 'theme': 'error' } )
        app.logger.error("Deleting gateway: Could not delete GW from db")
    return redirect("/")


@app.route('/gateway/<int:gateway_id>/', methods=['POST'])
def edit_gateway(gateway_id):
    gateway = GatewayInteractor.get(gateway_id)
    if gateway:
        from app.helpers.base64_helper import b64encode_quote
        authorization = b64encode_quote(request.form.get("authorization"))
        name = request.form.get("name")

        if authorization == gateway.authorization and name == gateway.name:
            flash("You didn't change anything!", category={ 'theme' : 'warning'} )
            return redirect("/gateway/%d/edit/" % (gateway_id, ))

        r = request_helper.check_gateway(gateway.address, authorization)

        if r != False:
            if r.status_code == 200:
                if r.text:
                    m = re.findall(r'<m2m:holderRef>(.*?)</m2m:holderRef>', r.text)
                    gateway.post_authorization = b64encode_quote(m[1])
                    gateway.active = True
                    gateway.name = name if name else m[1].split("//")[1].split(".")[0].lower()

                    gateway.save()

                    r = request_helper.check_device(gateway.address, authorization)

                    if r != False:
                        if r.status_code == 200:
                            flash("Device is already registered on gateway!", category={ 'theme': 'success' } )
                            gateway.device_registered = True
                            gateway.save()

                        elif r.status_code == 404:
                            flash("Device is not registered.", category={ 'theme': 'warning' } )
                else:
                    flash('Response was not a valid accessRights XML!', category={ 'theme': 'error' } )
                    app.logger.error("Editing gateway: Invalid accessRights XML")

            elif r.status_code == 400 or r.status_code == 404:
                flash("Wrong authorization URI! Gateway wasn't edited!", category={ 'theme': 'error' } )
                app.logger.error("Editing gateway: Wrong authorization URI")
                return edit_gateway_view(gateway_id)

    else:
        flash("Gateway doesn't exist!", category={ 'theme' : 'error'} )
        app.logger.error("Editing gateway: Gateway does not exist")
    return redirect('/')


@app.route('/gateway/<int:gateway_id>/edit/')
def edit_gateway_view(gateway_id):
    gateway = GatewayInteractor.get(gateway_id)
    if gateway:
        return render_template("gateway/edit.html", gateway=gateway)
    else:
        flash("Gateway doesn't exist!", category={ 'theme' : 'error'} )
        app.logger.error("Gateway editing: Gateway doesn't exist")
        return redirect('/')