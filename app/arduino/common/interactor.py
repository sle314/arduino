from app.arduino.common.models import Public_IP, Pin
from app.web import db

class PinInteractor:

	@staticmethod
	def get(pin):
		pin = Pin.query.filter(pin == pin).first()
		return pin

	@staticmethod
	def get_all():
		return Pin.query.all()


class PublicIPInteractor:

    @staticmethod
    def get():
        pub_ip = Public_IP.query.first()
        if pub_ip:
            return pub_ip
        return Public_IP()