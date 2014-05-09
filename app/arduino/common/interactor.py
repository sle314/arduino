# -*- coding: utf-8 -*-
from app.arduino.common.models import Public_IP

class PublicIPInteractor:

    @staticmethod
    def get():
        pub_ip = Public_IP.query.first()
        if pub_ip:
            return pub_ip
        return Public_IP()