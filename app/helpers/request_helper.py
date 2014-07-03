# -*- coding: utf-8 -*-
from app.web import app
from app.settings import local as settings
from requests.exceptions import ConnectionError, Timeout
import requests

from flask import flash, session
import os
import re

from app.arduino.sensor import SensorInteractor
from app.arduino.common import PublicIPInteractor
from app.arduino.hardware import PinInteractor


def call_arduino_path(path):
    try:
        r = requests.get("http://%s%s%s" % (
                settings.LOCAL,
                settings.REST_ROOT,
                path
                ),
            timeout = 5
        )

        return r

    except ConnectionError as e:
        flash("Cannot connect to %s!" % settings.LOCAL, category={'theme' : 'error'})
        app.logger.error("Calling arduino path: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={'theme' : 'error'})
        app.logger.error("Calling arduino path: %s" % (str(e), ))
        return False


def init_pin_modes():
    app.logger.info("----START init pin modes START----")
    sensors = SensorInteractor.get_all_active()
    if sensors:
        for sensor in sensors:
            if sensor.pin.arduino_pin[0] == "D":
                try:
                    requests.get("http://%s%s%s/%s/%s" % (
                            settings.LOCAL,
                            settings.REST_ROOT,
                            settings.MODE,
                            sensor.pin.pin[1:],
                            sensor.pin.io
                            ),
                        timeout = 5
                    )

                    app.logger.info("Pin %s mode successfully changed to %s!" % (sensor.pin.arduino_pin, sensor.pin.io))

                except ConnectionError:
                    app.logger.error("Cannot connect to %s!" % settings.IP_DNS)
                    continue

                except Timeout:
                    app.logger.error("Request timed out. Wrong IP?")
                    continue
    app.logger.info("----END init pin modes END----")


def change_pin_mode(pin, mode):
    try:
        r = requests.get("http://%s%s/%s/%s" % (
                settings.LOCAL,
                settings.MODE,
                pin,
                mode
                ),
            timeout = 5
        )
        return r

    except ConnectionError as e:
        flash("Cannot connect to %s!" % settings.LOCAL, category={ 'theme': 'error' } )
        app.logger.error("Changing pin mode: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Changing pin mode: %s" % (str(e), ))
        return False

def check_device(address, authorization):
    headers = {'Authorization': 'Basic %s' % authorization}

    try:
        r = requests.get("%s%s/%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID
                ),
            headers = headers,
            timeout = 5
        )
        return r

    except ConnectionError as e:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        app.logger.error("Checking device: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Checking device: %s" % (str(e), ))
        return False

def check_gateway(address, authorization):

    headers = {'Authorization': 'Basic %s' % authorization}
    try:

        r = requests.get("%s%s" % (
                address,
                settings.ACCESS_RIGHTS
            ),
            headers = headers,
            timeout = 5
        )
        return r

    except ConnectionError as e:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        app.logger.error("Checking gateway: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Checking gateway: %s" % (str(e), ))
        return False


def init_device(address, post_authorization):

    from app.arduino.hardware.interactor import PinInteractor

    xml = '<?xml version="1.0" encoding="UTF-8"?>\
<m2m:application appId="%(app_id)s" xmlns:m2m="http://uri.etsi.org/m2m">\
    <m2m:aPoC>http://%(public_ip)s/</m2m:aPoC>\
          <m2m:aPoCPaths>\
                    <m2m:aPoCPath>\
                              <m2m:path>/m2m/applications/%(app_id)s/retargeting1</m2m:path>\
                              <m2m:accessRightID>/m2m/accessRights/Locadmin_AR2</m2m:accessRightID>\
                    </m2m:aPoCPath>\
          </m2m:aPoCPaths>\
    <m2m:accessRightID>/m2m/accessRights/Locadmin_AR/</m2m:accessRightID>\
    <m2m:searchStrings>\
        <m2m:searchString>ETSI.ObjectType/ETSI.AN_APP</m2m:searchString>\
        <m2m:searchString>ETSI.ObjectTechnology/FER.%(app_id)s</m2m:searchString>\
    </m2m:searchStrings>\
</m2m:application>' % { "app_id" : settings.DEVICE_ID, "public_ip" : PublicIPInteractor.get().address }

    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    try:
        r = requests.post("%s%s" % (
                address,
                settings.APPLICATIONS
            ),
            headers = headers,
            timeout = 5,
            data = xml
        )

        return r
    except ConnectionError as e:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        app.logger.error("Device initialization: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Device initialization: %s" % (str(e), ))
        return False


def init_descriptor(address, post_authorization):
    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    xml = '<?xml version="1.0" encoding="UTF-8"?>\
<m2m:container m2m:id="DESCRIPTOR" xmlns:m2m="http://uri.etsi.org/m2m">\
   <m2m:accessRightID>/m2m/accessRights/Locadmin_AR</m2m:accessRightID>\
   <m2m:searchStrings>\
                   <m2m:searchString>ETSI.ObjectSemantic/OASIS.OBIX_1_1</m2m:searchString>\
   </m2m:searchStrings>\
   <m2m:maxNrOfInstances>1</m2m:maxNrOfInstances>\
</m2m:container>'
    try:
        r = requests.post("%s%s/%s%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS
            ),
            headers = headers,
            timeout = 5,
            data = xml
        )

        return r

    except ConnectionError as e:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        app.logger.error("Descriptor initialization: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Descriptor initialization: %s" % (str(e), ))
        return False

def init_sensor(address, post_authorization, sensor_identificator, method_path):

    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    xml = '<?xml version="1.0" encoding="UTF-8"?>\
<m2m:container m2m:id="%(sensor_id)s_%(method_path)s" xmlns:m2m="http://uri.etsi.org/m2m">\
    <m2m:accessRightID>/m2m/accessRights/Locadmin_AR</m2m:accessRightID>\
    <m2m:searchStrings>\
        <m2m:searchString>ETSI.ObjectSemantic/OASIS.OBIX_1_1</m2m:searchString>\
    </m2m:searchStrings>\
    <m2m:maxNrOfInstances>%(max_nr_vals)d</m2m:maxNrOfInstances>\
</m2m:container>' % { "sensor_id" : sensor_identificator, "max_nr_vals" : settings.MAX_NR_VALUES, "method_path" : method_path}

    try:
        r = requests.post("%s%s/%s%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS
            ),
            headers = headers,
            timeout = 5,
            data = xml
        )

        return r

    except ConnectionError as e:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        app.logger.error("Sensor initialization: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Sensor initialization: %s" % (str(e), ))
        return False

def send_descriptor(address, post_authorization):

    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    xml = '<?xml version="1.0" encoding="UTF-8"?>\
<obj xmlns="http://obix.org/ns/schema/1.1">\
    <str name="applicationID" val="%(app_id)s"/>\
    <list name="interfaces">\
        <obj>\
            <str name="interfaceID" val="Basic.Srv"/>\
        </obj>\
        <obj>\
            <str name="interfaceID" val="Identify.Srv"/>\
        </obj>' % { "app_id" : settings.DEVICE_ID }

    sensors = SensorInteractor.get_all_active()
    if sensors:

        sub_xml = ''

        for sensor in sensors:
            for sensor_method in sensor.sensor_methods:

                sub_xml = sub_xml + '<obj>\
                    <str name="interfaceID" val="%(sensor_identificator)s_%(method_path)s.Srv" />' % { "sensor_identificator" : sensor.identificator,"method_path" : sensor_method.method.path }
                if sensor_method.method.type in ["read", "write"]:
                    sub_xml = sub_xml + \
                    '<%(method_value_type)s href="%(sensor_href)s" name="m2mMeasuredValue" unit="obix:units/%(method_unit)s" />' %\
                        {
                            "method_value_type": sensor_method.method.value_type,
                            "method_unit" : sensor_method.method.unit,
                            "sensor_href" : '%s/%s%s/%s_%s%s%s' % (settings.APPLICATIONS, settings.DEVICE_ID, settings.CONTAINERS, sensor.identificator, sensor_method.method.path, settings.CONTENT_INSTANCES, settings.LATEST_CONTENT)
                        }
                if sensor_method.method.type in ["write", "call"]:
                    path = sensor_method.method.path
                    if sensor_method.method.type == "write":
                        path += "/[value-to-be-written]"
                    sub_xml = sub_xml + \
                        '<op type="%(method_type)s" name="%(method_name)s" href="/m2m/applications/%(app_id)s/retargeting1/sensors/%(sensor_id)s/%(method_path)s" />'\
                        % { "method_type" : sensor_method.method.type, "method_name" : sensor_method.method.path, "method_path" : path, "app_id" : settings.DEVICE_ID, "sensor_id" : sensor.identificator}
                sub_xml = sub_xml + '</obj>'

                init_sensor(address, post_authorization, sensor.identificator, sensor_method.method.path)

        xml = xml + sub_xml

    else:
        flash("No active sensors to send values for after DESCRIPTOR initiation!", category={ 'theme' : 'warning' } )

    xml = xml + '</list></obj>'

    try:
        r = requests.post("%s%s/%s%s%s%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS,
                settings.DESCRIPTOR,
                settings.CONTENT_INSTANCES
            ),
            headers = headers,
            timeout = 5,
            data = xml
        )

        return r

    except ConnectionError as e:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        app.logger.error("Sending descriptor: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Sending descriptor: %s" % (str(e), ))
        return False


def get_sensor_value(sensor, method_path):
    try:
        r = requests.get("http://%s%s/%s/%s/%s/%s" % (
                settings.LOCAL,
                settings.REST_ROOT,
                sensor.module.hardware.path,
                sensor.module.path,
                method_path,
                sensor.pin.pin
            ),
            timeout = 5
        )

        if r.status_code == 200:
            return r.text

    except ConnectionError as e:
        flash("Cannot connect to device!", category={ 'theme': 'error' } )
        app.logger.error("Getting value for sensor: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Getting value for sensor: %s" % (str(e), ))
        return False

    return False


def send_sensor_value(address, post_authorization, sensor_identificator, method_path, value):

    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    xml = '<?xml version="1.0" encoding="UTF-8" ?>\
<real xmlns="http://obix.org/ns/schema/1.1" val="%s" />' % str(value)

    try:
        r = requests.post("%s%s/%s%s/%s%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS,
                "%s_%s" % (sensor_identificator, method_path),
                settings.CONTENT_INSTANCES
            ),
            headers = headers,
            timeout = 5,
            data = xml
        )

        return r

    except ConnectionError as e:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        app.logger.error("Sending sensor value to GW: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Sending sensor value to GW: %s" % (str(e), ))
        return False


def delete_sensor(address, post_authorization, sensor_identificator, method_path):
    headers = {'Authorization': 'Basic %s' % post_authorization}

    try:
        r = requests.delete("%s%s/%s%s/%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS,
                "%s_%s" % (sensor_identificator, method_path)
            ),
            headers = headers,
            timeout = 5
        )

        return r

    except ConnectionError as e:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        app.logger.error("Deleting sensor from GW: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Deleting sensor from GW: %s" % (str(e), ))
        return False


def delete_device(address, post_authorization):

    headers = {'Authorization': 'Basic %s' % post_authorization}

    try:
        r = requests.delete("%s%s/%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID
            ),
            headers = headers,
            timeout = 5
        )

        return r

    except ConnectionError as e:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        app.logger.error("Deleting device from GW: %s" % (str(e), ))
        return False

    except Timeout as e:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        app.logger.error("Deleting device from GW: %s" % (str(e), ))
        return False
