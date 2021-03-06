# -*- coding: utf-8 -*-
from app.arduino.gateway.models import Gateway
from sqlalchemy import and_

class GatewayInteractor:

    @staticmethod
    def get(gateway_id):
        gateway = Gateway.query.filter(Gateway.id==gateway_id).first()
        return gateway

    @staticmethod
    def get_all():
        gateways = Gateway.query.all()
        return gateways

    @staticmethod
    def get_all_device_registered():
        gateways = Gateway.query.filter(and_( Gateway.device_registered==True, Gateway.active==True )).all()
        return gateways

    @staticmethod
    def check_address(address):
        if Gateway.query.filter(Gateway.address==address).first():
            return True
        return False

    @staticmethod
    def delete(gateway_id):
        gateway = Gateway.query.filter(Gateway.id==gateway_id).first()
        if gateway:
            gateway.delete()
            return True
        return False
