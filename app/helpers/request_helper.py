from app.settings import local as settings
from requests.exceptions import ConnectionError, Timeout
import requests
import xml.etree.ElementTree as ET
from flask import flash
import os

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
        flash("Cannot connect to gateway %s!" % gateway.address, category={ 'theme': 'error' } )
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
    ET.register_namespace("m2m", "http://uri.etsi.org/m2m")
    tree = ET.parse('%s/app/web/xml/device.xml' % os.getcwd())

    root = tree.getroot()
    root.set('appId', settings.DEVICE_ID)

    search_string = ET.SubElement(root, 'm2m:searchString')
    search_string.text = 'ETSI.ObjectTechnology/ACTILITY.%s' % settings.DEVICE_ID

    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    try:
        r = requests.post("%s%s" % (
                address,
                settings.APPLICATIONS
            ),
            headers = headers,
            timeout = 5,
            data = ET.tostring(root)
        )

        return r
    except ConnectionError:
        flash("Cannot connect to gateway %s!" % gateway.address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False


def init_descriptor(address, post_authorization):
    ET.register_namespace("m2m", "http://uri.etsi.org/m2m")
    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    tree = ET.parse('%s/app/web/xml/device_descriptor.xml' % os.getcwd())

    try:
        r = requests.post("%s%s/%s%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS
            ),
            headers = headers,
            timeout = 5,
            data = ET.tostring(tree.getroot())
        )

        return r

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % gateway.address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False

def init_sensor(address, post_authorization, sensor_identificator):
    ET.register_namespace("m2m", "http://uri.etsi.org/m2m")
    tree = ET.parse('%s/app/web/xml/sensor.xml' % os.getcwd())
    root = tree.getroot()

    root.set('m2m:id', sensor_identificator)
    root[2].text = str(settings.MAX_NR_VALUES)

    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    try:
        r = requests.post("%s%s/%s%s" % (
                address,
                settings.APPLICATIONS,
                settings.DEVICE_ID,
                settings.CONTAINERS
            ),
            headers = headers,
            timeout = 5,
            data = ET.tostring(root)
        )

        return r

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % gateway.address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False

def send_descriptor(address, post_authorization):

    ET.register_namespace("", "http://obix.org/ns/schema/1.1")
    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    tree = ET.parse('%s/app/web/xml/device_descriptor_instance.xml' % os.getcwd())

    root = tree.getroot()
    root[0].set('val', settings.DEVICE_ID)

    sensors = SensorInteractor.get_all_active()
    if sensors:

        type = []
        n = 1

        for sensor in sensors:
            obj = ET.SubElement(root[1], 'obj')
            str = ET.SubElement(obj, 'str')
            real = ET.SubElement(obj, 'real')
            str.set('name', 'interfaceID')

            sensor_type = sensor.type
            if sensor_type in type:
                sensor_type = '%s%02d' % ( sensor.type, n)
                n = n + 1
            str.set('val', '%s.Srv' % sensor_type)
            type.append(sensor_type)

            real.set('name', 'm2mMeasuredValue')
            real.set('unit', 'obix:units/%s' % sensor.unit)
            real.set('href', '%s/%s%s/%s%s%s' % (settings.APPLICATIONS, settings.DEVICE_ID, settings.CONTAINERS, sensor.identificator, settings.CONTENT_INSTANCES, settings.LATEST_CONTENT))

            init_sensor(address, post_authorization, sensor.identificator)

    else:
        flash("No active sensors to send values for after DESCRIPTOR initiation!", category={ 'theme' : 'warning' } )

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
            data = ET.tostring(root)
        )

        return r

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % gateway.address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False


def send_sensor_value(address, post_authorization, sensor_identificator, value):

    ET.register_namespace("", "http://obix.org/ns/schema/1.1")

    headers = {'Authorization': 'Basic %s' % post_authorization, "content-type":"application/xml"}

    tree = ET.parse('%s/app/web/xml/sensor_value.xml' % os.getcwd())
    root = tree.getroot()

    root.set('val', str(value))

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
            data = ET.tostring(root)
        )

        return r

    except ConnectionError:
        flash("Cannot connect to gateway %s!" % gateway.address, category={ 'theme': 'error' } )
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
        flash("Cannot connect to gateway %s!" % gateway.address, category={ 'theme': 'error' } )
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
        flash("Cannot connect to gateway %s!" % gateway.address, category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False
