# -*- coding: utf-8 -*-
from . import app
from app.settings import local as settings
import os

from flask import render_template, request, session, redirect, flash, json
from requests.exceptions import ConnectionError, Timeout
from app.arduino.sensor import SensorInteractor
from app.arduino.gateway import Gateway, GatewayInteractor
from app.helpers.request_helper import check_gateway, check_device, init_device, init_descriptor, send_descriptor, init_sensor, send_sensor_value, delete_device

import requests
import re

@app.route('/gateway/', methods=['POST'])
def gateway():

    gateway = Gateway()

    address = request.form.get("address")
    address = address if "http://" in address else "http://%s" % address

    from app.helpers.base64_helper import b64encode_quote
    authorization = b64encode_quote(request.form.get("authorization"))

    r = check_gateway(address, authorization)

    if r != False:
        if r.status_code == 200:
            session['error'] = False

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

                r = check_device(address, authorization)

                if r != False:
                    if r.status_code == 200:
                        flash("Device is already registered on gateway!", category={ 'theme': 'success' } )
                        gateway.device_registered = True
                        gateway.save()

                    elif r.status_code == 404:
                        flash("Device is not registered.", category={ 'theme': 'warning' } )
            else:
                flash('Response was not a valid accessRights XML!', category={ 'theme': 'error' } )

        elif r.status_code == 400 or r.status_code == 404:
            flash("Wrong authorization URI! Gateway wasn't added!", category={ 'theme': 'error' } )

    session['error'] = True
    return redirect('/')


@app.route('/gateway/<int:gateway_id>/register_device/')
def register_device_on_gateway(gateway_id):
    gateway = GatewayInteractor.get(gateway_id)
    if gateway:
        r = init_device(gateway.address, gateway.post_authorization)

        if r != False:
            if r.status_code == 201 or r.status_code == 409:

                r = init_descriptor(gateway.address, gateway.post_authorization)

                if r != False:
                    print r.status_code

                    r = send_descriptor(gateway.address, gateway.post_authorization)

                    if r != False:
                        sensors = SensorInteractor.get_all_active()

                        if sensors:
                            for sensor in sensors:
                                if sensor.active:
                                    r = init_sensor(gateway.address, gateway.post_authorization, sensor.identificator)
                                    if r != False:
                                        sensor.save()
                                        r = send_sensor_value(gateway.address, gateway.post_authorization, sensor.identificator, sensor.value)

                        flash('Device successfully registered!', category={ 'theme': 'success' } )
                        gateway.device_registered = True
                        gateway.save()

            elif r.status_code == 400 or r.status_code == 401:
                flash('Wrong authorization for registration!', category={ 'theme': 'error' } )

            else:
                flash('Something went wrong!', category={ 'theme': 'error' } )
    else:
        flash("Gateway does not exist!", category={ 'theme': 'error' } )

    return redirect("/")


@app.route('/gateway/<int:gateway_id>/unregister_device/')
def remove_device_from_gateway(gateway_id):

    gateway = GatewayInteractor.get(gateway_id)
    if gateway:

        r = delete_device(gateway.address, gateway.post_authorization)

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
    else:
        flash("Gateway does not exist!", category={ 'theme': 'error' } )

    return redirect('/')


@app.route('/gateway/delete/', methods=['POST'])
def remove_gateway():
    gateway_id = request.form.get('gateway_id')
    remove_device_from_gateway(gateway_id)
    if GatewayInteractor.delete(gateway_id):
        flash("Gateway successfully removed!", category={ 'theme': 'success' } )
    else:
        flash("Could not remove gateway!", category={ 'theme': 'error' } )
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

        r = check_gateway(gateway.address, authorization)

        if r != False:
            if r.status_code == 200:

                if r.text:
                    m = re.findall(r'<m2m:holderRef>(.*?)</m2m:holderRef>', r.text)
                    gateway.post_authorization = b64encode_quote(m[1])
                    gateway.active = True
                    gateway.name = name if name else m[1].split("//")[1].split(".")[0].lower()

                    gateway.save()

                    r = check_device(gateway.address, authorization)

                    if r != False:
                        if r.status_code == 200:
                            flash("Device is already registered on gateway!", category={ 'theme': 'success' } )
                            gateway.device_registered = True
                            gateway.save()

                        elif r.status_code == 404:
                            flash("Device is not registered.", category={ 'theme': 'warning' } )
                else:
                    flash('Response was not a valid accessRights XML!', category={ 'theme': 'error' } )

            elif r.status_code == 400 or r.status_code == 404:
                flash("Wrong authorization URI! Gateway wasn't edited!", category={ 'theme': 'error' } )
                return edit_gateway_view(gateway_id)

    else:
        flash("Gateway doesn't exist!", category={ 'theme' : 'error'} )
    return redirect('/')


@app.route('/gateway/<int:gateway_id>/edit/')
def edit_gateway_view(gateway_id):
    gateway = GatewayInteractor.get(gateway_id)
    if gateway:
        return render_template("gateway/edit.html", gateway=gateway)
    else:
        flash("Gateway doesn't exist!", category={ 'theme' : 'error'} )
        return redirect('/')