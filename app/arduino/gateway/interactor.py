from app.arduino.gateway.models import Gateway
from app.web import db

class GatewayInteractor:

    @staticmethod
    def get(gateway_id):
        gateway = Gateway.query.filter_by(id=gateway_id).first()
        return gateway

    @staticmethod
    def get_all():
        gateways = Gateway.query.all()
        return gateways

    @staticmethod
    def delete(gateway_id):
        gateway = Gateway.query.filter_by(id=gateway_id).first()
        if gateway:
            db.session.delete(gateway)
            db.session.commit()
            return True
        return False
