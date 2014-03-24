from app.arduino.sensor.models import Sensor
# import threading
from app.web import db

class SensorInteractor:

    @staticmethod
    def get(sensor_id):
        sensor = Sensor.query.filter_by(id=sensor_id).first()
        return sensor

    @staticmethod
    def get_all():
        sensors = Sensor.query.all()
        return sensors

    @staticmethod
    def get_all_active():
        sensors = Sensor.query.filter_by(active=True).all()
        return sensors

    @staticmethod
    def register(sensor_id):
        # threading.Timer(5, register(sensor_id)).start()
        print "registered"

    @staticmethod
    def delete(sensor_id):
        sensor = Sensor.query.filter_by(id=sensor_id).first()
        if sensor:
            db.session.delete(sensor)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_by_identificator(identificator):
        sensor = Sensor.query.filter_by(identificator=identificator).first()
        return sensor

    @staticmethod
    def set_value(sensor_id, value):
        sensor = Sensor.query.filter_by(id=sensor_id).first()
        sensor.value = str(value)
        sensor.save()
