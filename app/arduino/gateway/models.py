# -*- coding: utf-8 -*-
from app.web import db

class Gateway(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    address = db.Column(db.String(100), unique=True)
    authorization = db.Column(db.String(200))
    post_authorization = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=False)
    device_registered = db.Column(db.Boolean, default=False)

    def __str__(self):
        return "%s %s %s" % (self.id, self.authorization, self.address)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'address': self.address,
            'authorization': self.authorization,
        }
