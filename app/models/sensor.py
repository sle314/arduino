# -*- coding: utf-8 -*-
from random import randrange
from app.db import db

class Sensor(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), unique=True)
    unit = db.Column(db.String(120), unique=True)
    value = db.Column(db.String(120), unique=True)

    def __init__(self, id):
        self.id = id
        self.unit = ""
        self.type = ""
        self.value = 0

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
            'value': self.value
        }
