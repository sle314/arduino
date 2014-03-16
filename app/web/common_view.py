# -*- coding: utf-8 -*-
from . import app
from app.settings import local as settings

from flask import render_template, request, session, redirect, flash
from requests.exceptions import ConnectionError, Timeout
import requests

@app.before_request
def before_request():
    if request.endpoint != "static":
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
            headers = headers,
            timeout = 5
        )

        if r.status_code == 400:
            session['theme'] = 'error'
            flash("Could not authenticate!")
            return redirect("/")

        if r.status_code == 200:
            registered = True        
            session['theme'] = 'success'
            flash("Gateway set!")
            flash("App is already registered!")        

        elif r.status_code == 404:
            session['theme'] = 'warning'
            flash("Either app is not registered or authorization is invalid!")

        session['gateway'] = gateway
        session['auth'] = auth

        return render_template("/device/register.html", registered = registered)

    except ConnectionError:
        flash("Cannot connect to specified gateway!")
        
    except Timeout:
        flash("Request timed out. Wrong IP?")
            
    session['theme'] = 'error'
    return redirect("/")

    
