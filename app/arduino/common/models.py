# -*- coding: utf-8 -*-
from app.web import db

class Pin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pin = db.Column(db.String(3), unique=True)
    last_io = db.Column(db.String(10), default="output")

    def save(self):
    	db.session.add(self)
        db.session.commit()

    def get_last_io(self):
    	return self.last_io


class Public_IP(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(100), unique=True)

    def __str__(self):
        return "%s %s %s" % (self.id, self.authorization, self.address)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_address(self):
        return self.address
