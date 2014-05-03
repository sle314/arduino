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

    except ConnectionError:
        flash("Cannot connect to %s!" % settings.LOCAL, category={'theme' : 'error'})
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={'theme' : 'error'})
        return False


def get_from_pin(mode, pin):
    try:
        r = requests.get("http://%s%s/%s/%s" % (
                settings.LOCAL,
                settings.REST_ROOT,
                mode,
                pin
                ),
            timeout = 5
        )

        return r

    except ConnectionError:
        flash("Cannot connect to %s!" % settings.LOCAL, category={'theme' : 'error'})
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={'theme' : 'error'})
        return False

def write_to_pin(mode, pin, value):
    try:
        r = requests.get("http://%s%s/%s/%s/%s" % (
                settings.LOCAL,
                settings.REST_ROOT,
                mode,
                pin,
                value
                ),
            timeout = 5
        )

        flash("Pin %s value successfully written!" % pin, category={'theme' : 'success'} );
        return r

    except ConnectionError:
        flash("Cannot connect to %s!" % settings.LOCAL, category={'theme' : 'error'})
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={'theme' : 'error'})
        return False

def init_pin_modes():
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

                    print "Pin %s mode successfully changed to %s!" % (sensor.pin.arduino_pin, sensor.pin.io)

                except ConnectionError:
                    print "Cannot connect to %s!" % settings.IP_DNS
                    break

                except Timeout:
                    print "Request timed out. Wrong IP?"
                    break

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

    except ConnectionError:
        flash("Cannot connect to %s!" % settings.LOCAL, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
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

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
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

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False


def init_device(address, post_authorization):

    from app.arduino.hardware.interactor import PinInteractor

    xml = '<?xml version="1.0" encoding="UTF-8"?>\
<m2m:application appId="%(app_id)s" xmlns:m2m="http://uri.etsi.org/m2m">\
    <m2m:aPoC>http://%(public_ip)s:%(port)s/</m2m:aPoC>\
          <m2m:aPoCPaths>\
                    <m2m:aPoCPath>\
                              <m2m:path>/m2m/applications/%(app_id)s/retargeting1</m2m:path>\
                              <m2m:accessRightID>/m2m/accessRights/Locadmin_AR2</m2m:accessRightID>\
                    </m2m:aPoCPath>\
          </m2m:aPoCPaths>\
    <m2m:accessRightID>/m2m/accessRights/Locadmin_AR/</m2m:accessRightID>\
    <m2m:searchStrings>\
        <m2m:searchString>ETSI.ObjectType/ETSI.AN_NODE</m2m:searchString>\
        <m2m:searchString>ETSI.ObjectTechnology/ACTILITY.%(app_id)s</m2m:searchString>\
    </m2m:searchStrings>\
</m2m:application>' % { "app_id" : settings.DEVICE_ID, "public_ip" : PublicIPInteractor.get().address, "port" : settings.PORT }

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
    except ConnectionError:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
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

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
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

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
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
    print sensors
    if sensors:

        # type = []
        # n = 1
        sub_xml = ''

        for sensor in sensors:
            for sensor_method in sensor.sensor_methods:

                # sensor_type = sensor.type
                # if sensor_type in type:
                #     sensor_type = '%s%02d' % ( sensor.type, n)
                #     n = n + 1
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
                        path += "/<value-to-be-written>"
                    sub_xml = sub_xml + \
                        '<op type="%(method_type)s" name="%(method_name)s" href="/m2m/applications/%(app_id)s/retargeting1/sensors/%(sensor_id)s/%(method_path)s" />'\
                        % { "method_type" : sensor_method.method.type, "method_name" : sensor_method.method.path, "method_path" : path, "app_id" : settings.DEVICE_ID, "sensor_id" : sensor.identificator}
                sub_xml = sub_xml + '</obj>'

                # type.append(sensor_type)

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

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False

# def get_sensor_value(pin):
#     try:
#         r = requests.get("http://localhost/data/get/%s" % pin,
#             timeout = 10
#         )

#         from flask import json

#         return json.loads(r.text)['value']

#     except ConnectionError:
#         flash("Cannot connect to device!", category={ 'theme': 'error' } )
#         return False

#     except Timeout:
#         flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
#         return False

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

        return r.text

    except ConnectionError:
        flash("Cannot connect to device!", category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False

# def get_sensor_values():
#     try:
#         r = requests.get("http://localhost/data/get",
#             timeout = 5
#         )

#         from flask import json

#         return json.loads(r.text)['value']

#     except ConnectionError:
#         # flash("Cannot connect to device!", category={ 'theme': 'error' } )
#         return False

#     except Timeout:
#         # flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
#         return False


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

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False


def toggle_sensor(type, pin):

    r = get_from_pin(type, pin)

    if r.status_code == 200:
        value = "0"
        if r.text == "0":
            value = "1"

        r = write_to_pin(type, pin, value)

        return r


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

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
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

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False
