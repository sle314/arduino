# -*- coding: utf-8 -*-
from . import app
from app.settings import local as settings

from flask import render_template, request, session, redirect, flash
from requests.exceptions import ConnectionError
import requests

@app.before_request
def before_request():
    print request
    if 'gateway' not in session:
        session['gateway'] = settings.GATEWAY
        from app.helpers.base64_helper import b64encode_quote
        session['auth'] = b64encode_quote(settings.AUTH)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register/', methods=['POST'])
def register():
    registered = False
    gateway = request.form.get("gateway")
    gateway = gateway if "http://" in gateway else "http://%s" % gateway

    from app.helpers.base64_helper import b64encode_quote
    auth = b64encode_quote(request.form.get("auth"))

    headers = {'Authorization': 'Basic %s' % auth}

    try:
        r = requests.get("%s%s/%s" % (
                gateway,
                settings.APPLICATIONS,
                settings.DEVICE_ID
            ),
            headers = headers
        )
    except ConnectionError:
        flash("Cannot connect to specified gateway!")
        session['theme'] = 'error'

    if r.status_code == 200:
        registered = True
        session['gateway'] = gateway
        session['auth'] = auth
        session['theme'] = 'success'
        flash("Gateway set!")
        flash("Gateway already registered!")

        return render_template("/device/register.html", registered = registered)

    elif r.status_code == 404:
        print r
        flash("Could not authenticate!")

    session['theme'] = 'error'
    return redirect("/")




