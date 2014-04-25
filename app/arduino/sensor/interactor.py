from app.arduino.sensor.models import Sensor
from app.arduino.hardware import Pin
# import threading
from app.web import db
from sqlalchemy import and_

class SensorInteractor:

    @staticmethod
    def get(sensor_id):
        sensor = Sensor.query.filter(Sensor.id==sensor_id).first()
        return sensor

    @staticmethod
    def get_all():
        sensors = Sensor.query.all()
        return sensors

    @staticmethod
    def get_all_active():
        sensors = Sensor.query.filter(Sensor.active==True).all()
        return sensors

    @staticmethod
    def get_active_for_pin(pin):
        sensors = Sensor.query.join(Pin).filter(and_(Pin.arduino_pin==pin, Sensor.active==True)).all()
        return sensors

    @staticmethod
    def delete(sensor_id):
        sensor = Sensor.query.filter(Sensor.id==sensor_id).first()
        if sensor:
            db.session.delete(sensor)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_by_identificator(identificator):
        sensor = Sensor.query.filter(Sensor.identificator==identificator).first()
        return sensor

    @staticmethod
    def set_value(sensor_id, value):
        sensor = Sensor.query.filter(Sensor.id==sensor_id).first()
        sensor.value = str(value)
        sensor.save()
