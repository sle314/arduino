# -*- coding: utf-8 -*-
from app.web import db


class Hardware(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    path = db.Column(db.String(50))

    def __init__(self, name, path):
        self.name = name
        self.path = path

    def save(self):
        db.session.add(self)
        db.session.commit()


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50))
    name = db.Column(db.String(50))
    path = db.Column(db.String(50))
    hardware_id = db.Column(db.Integer, db.ForeignKey('hardware.id'))
    hardware = db.relationship('Hardware', backref=db.backref('modules', lazy='dynamic'))
    io = db.Column(db.String(10), default="input")
    ad = db.Column(db.String(10), default="digital")

    def __init__(self, data):
        self.name = data['name']
        self.hardware_id = data['hw_id']
        self.io = data['io']
        self.ad = data['ad']
        self.path = data['path']
        self.type = data['type']

    def save(self):
        db.session.add(self)
        db.session.commit()


class Pin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pin = db.Column(db.String(20))
    arduino_pin = db.Column(db.String(3))
    io = db.Column(db.String(10), default="input")
    ad = db.Column(db.String(10), default="digital")

    hardware_id = db.Column(db.Integer, db.ForeignKey('hardware.id'))
    hardware = db.relationship('Hardware', backref=db.backref('pins', lazy='dynamic'))

    def __init__(self, data):
        self.pin = data['pin']
        self.hardware_id = data['hw_id']
        self.arduino_pin = data['arduino_pin']
        self.io = data['io']
        self.ad = data['ad']

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'pin': self.pin
        }



class Method(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module = db.relationship('Module', backref=db.backref('methods', lazy='dynamic'))

    name = db.Column(db.String(50))
    path = db.Column(db.String(50))
    type = db.Column(db.String(10), default="read")

    value = db.Column(db.String(100), default="0")
    unit = db.Column(db.String(20))

    def __init__(self, data):
        self.name = data['name']
        self.type = data['type']
        self.module_id = data['mod_id']
        self.unit = data['unit']
        self.path = data['path']

    def save(self):
        db.session.add(self)
        db.session.commit()