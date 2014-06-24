# -*- coding: utf-8 -*-
from app.web import db
import datetime

class SensorMethods(db.Model):

    sensor_id = db.Column(db.Integer, db.ForeignKey('sensor.id'), primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey('method.id'), primary_key=True)
    value = db.Column(db.String(100))
    method = db.relationship("Method")

    def save(self):
        db.session.add(self)
        db.session.commit()


class Sensor(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50), default="Sensing device")
    identificator = db.Column(db.String(100), unique=True)
    active = db.Column(db.Boolean, default=False)
    pin_id = db.Column(db.Integer, db.ForeignKey('pin.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    timestamp = db.Column(db.DateTime)

    pin = db.relationship('Pin')
    module = db.relationship('Module')

    sensor_methods = db.relationship("SensorMethods", cascade='all')

    def __str__(self):
        return "%s %s %s %s" % (self.id, self.type, self.identificator, self.active)

    def save(self):
        self.timestamp = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'type': self.type,
            'identificator': self.identificator
        }
