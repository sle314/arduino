from app.arduino.sensor.models import Sensor, SensorMethods
from app.arduino.hardware import Pin
from sqlalchemy import and_, asc, desc

class SensorInteractor:

    @staticmethod
    def get(sensor_id):
        sensor = Sensor.query.filter(Sensor.id==sensor_id).first()
        return sensor

    @staticmethod
    def get_all():
        sensors = Sensor.query.order_by(Sensor.active.desc(), Sensor.identificator.asc()).all()
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
            sensor.delete()
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


class SensorMethodsInteractor:

    @staticmethod
    def get(sensor_id, method_id):
        return SensorMethods.query.filter(and_( SensorMethods.sensor_id==sensor_id, SensorMethods.method_id==method_id )).first()

    @staticmethod
    def delete_all_for_sensor(sensor_id):
        from app.web import db
        db.session.query(SensorMethods).filter(SensorMethods.sensor_id == sensor_id).delete()
