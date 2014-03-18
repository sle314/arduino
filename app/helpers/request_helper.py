from app.settings import local as settings
from requests.exceptions import ConnectionError, Timeout
import requests
from flask import flash

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
        flash("Cannot connect to specified gateway!", category={ 'theme': 'error' } )
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
        flash("Cannot connect to specified gateway!", category={ 'theme': 'error' } )
        return False

    except Timeout:
        flash("Request timed out. Wrong IP?", category={ 'theme': 'error' } )
        return False