from app.arduino.sensor.models import Sensor
import threading

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
    def register(sensor_id):
        threading.Timer(5, register(sensor_id)).start()
        print "bravo"