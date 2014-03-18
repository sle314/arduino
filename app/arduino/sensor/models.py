# -*- coding: utf-8 -*-
from random import randrange
from app.web import db

class Sensor(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(10), default="digital")
    unit = db.Column(db.String(120))
    value = db.Column(db.String(120))
    identificator = db.Column(db.String(100), unique=True)
    registered = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=False)
    measuring = db.Column(db.String(80))
    pin = db.Column(db.Integer, default=0)

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
