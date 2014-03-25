# -*- coding: utf-8 -*-
from app.settings import local as settings

from app.web import app

from flask import render_template, request
from app.arduino.gateway import GatewayInteractor

@app.before_request
def before_request():
    if request.endpoint != "static":
        pass


@app.route('/')
def index():
    return render_template("gateway/index.html", settings=settings, gateways=GatewayInteractor.get_all())


@app.route('/cron/')
def cron():
    gw = GatewayInteractor.get(1)
    gw.name = "goood"
    gw.save()
    return True
