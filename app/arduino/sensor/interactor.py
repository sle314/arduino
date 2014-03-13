from app.arduino.sensor.models import Sensor

class SensorInteractor:

    @staticmethod
    def get(sensor_id):
        sensor = Sensor.query.filter_by(id=sensor_id).first()
        return sensor

    @staticmethod
    def get_all():
        sensors = Sensor.query.all()
        return sensors