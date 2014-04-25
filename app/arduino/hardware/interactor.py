from app.arduino.hardware.models import Pin, Module, Method
from sqlalchemy import and_

class ModuleInteractor:

    @staticmethod
    def get_all():
        return Module.query.all()

    @staticmethod
    def get_pins(module_id):
        module = Module.query.filter(Module.id == module_id).first()
        pins = Pin.query.filter(and_(Pin.io == module.io, Pin.ad == module.ad, Pin.hardware_id == module.hardware_id))
        return pins


class PinInteractor:

    @staticmethod
    def get(pin_id):
        return Pin.query.filter(Pin.id == pin_id).first()

    @staticmethod
    def get_by_name(pin):
        return Pin.query.filter(Pin.pin == pin).first()

    @staticmethod
    def get_all():
        return Pin.query.all()


class MethodInteractor:

    @staticmethod
    def get(method_id):
        return Method.query.filter(Method.id == method_id).first()

    @staticmethod
    def get_by_path(method_path, module_id):
        return Method.query.filter(and_(Method.path == method_path, Method.module_id == module_id)).first()

    @staticmethod
    def get_all():
        return Method.query.all()