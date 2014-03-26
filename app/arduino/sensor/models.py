# -*- coding: utf-8 -*-
from app.web import db

class Sensor(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(100), default="sensing_device")
    unit = db.Column(db.String(120), default="")
    value = db.Column(db.String(120), default="0")
    min_value = db.Column(db.Float, default=0.0)
    max_value = db.Column(db.Float, default=1.0)
    toggle = db.Column(db.Boolean, default=False)
    identificator = db.Column(db.String(100), unique=True)
    active = db.Column(db.Boolean, default=False)
    pin = db.Column(db.String(3), default="A0")
    threshold = db.Column(db.Float, default=0.0)

    def __str__(self):
        return "%s %s %s %s" % (self.id, self.type, self.value, self.unit)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'unit': self.unit,
            'type': self.type,
            'value': self.value,
            'identificator': self.identificator
        }
