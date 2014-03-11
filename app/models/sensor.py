# -*- coding: utf-8 -*-
from random import randrange

class Sensor:

    def __init__(self, id):
        self.id = id
        self.unit = ""
        self.type = ""
        self.value = 0

    def __str__(self):
        return "%s %s %s %s" % (self.id, self.type, self.value, self.unit)

    def to_json(self):
        return {
            'id': self.id,
            'unit': self.unit,
            'type': self.type,
            'value': self.value
        }
