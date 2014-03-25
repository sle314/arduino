from app.settings import local as settings
from requests.exceptions import ConnectionError, Timeout
import requests

from flask import flash
import os
import re

from app.arduino.sensor import SensorInteractor

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

    xml = '<?xml version="1.0" encoding="UTF-8"?>\
<m2m:application appId="%(app_id)s" xmlns:m2m="http://uri.etsi.org/m2m">\
    <m2m:accessRightID>/m2m/accessRights/Locadmin_AR/</m2m:accessRightID>\
    <m2m:searchStrings>\
        <m2m:searchString>ETSI.ObjectType/ETSI.AN_NODE</m2m:searchString>\
        <m2m:searchString>ETSI.ObjectTechnology/ACTILITY.%(app_id)s</m2m:searchString>\
    </m2m:searchStrings>\
</m2m:application>' % { "app_id" : settings.DEVICE_ID }

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

def init_sensor(address, post_authorization, sensor_identificator):

    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    xml = '<?xml version="1.0" encoding="UTF-8"?>\
<m2m:container m2m:id="%(sensor_id)s" xmlns:m2m="http://uri.etsi.org/m2m">\
    <m2m:accessRightID>/m2m/accessRights/Locadmin_AR</m2m:accessRightID>\
    <m2m:searchStrings>\
        <m2m:searchString>ETSI.ObjectSemantic/OASIS.OBIX_1_1</m2m:searchString>\
    </m2m:searchStrings>\
    <m2m:maxNrOfInstances>%(max_nr_vals)d</m2m:maxNrOfInstances>\
</m2m:container>' % { "sensor_id" : sensor_identificator, "max_nr_vals" : settings.MAX_NR_VALUES}

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

    if sensors:

        type = []
        n = 1
        sub_xml = ''

        for sensor in sensors:

            sensor_type = sensor.type
            if sensor_type in type:
                sensor_type = '%s%02d' % ( sensor.type, n)
                n = n + 1
            sub_xml = sub_xml + '<obj>\
            <str name="interfaceID" val="%(sensor_type)s.Srv" />\
            <real href="%(sensor_href)s" name="m2mMeasuredValue" unit="obix:units/%(sensor_unit)s" />\
        </obj>' % { "sensor_type" : sensor_type,
                    "sensor_unit" : sensor.unit,
                    "sensor_href" : '%s/%s%s/%s%s%s' % (settings.APPLICATIONS, settings.DEVICE_ID, settings.CONTAINERS, sensor.identificator, settings.CONTENT_INSTANCES, settings.LATEST_CONTENT)
                }

            type.append(sensor_type)

            init_sensor(address, post_authorization, sensor.identificator)

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

def get_sensor_value(pin):
    try:
        r = requests.get("http://localhost/data/get/%s" % pin,
            timeout = 10
        )

        from flask import json

        return json.loads(r.text)['value']

    except ConnectionError:
        flash("Cannot connect to device!", category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False


def send_sensor_value(address, post_authorization, sensor_identificator, value):

    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    xml = '<?xml version="1.0" encoding="UTF-8" ?>\
<real xmlns="http://obix.org/ns/schema/1.1" val="%s" />' % str(value)

    try:
        r = requests.post("%s%s/%s%s/%s%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS,
                sensor_identificator,
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


def delete_sensor(address, post_authorization, sensor_identificator):
    headers = {'Authorization': 'Basic %s' % post_authorization}

    try:
        r = requests.delete("%s%s/%s%s/%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS,
                sensor_identificator
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
