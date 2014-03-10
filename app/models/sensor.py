class Sensor:

    def __init__(self, id=0, type="Sensor", value=0, unit=None):
        self.id = id
        self.type = type
        self.value = value
        self.unit = unit

    def __str__(self):
        return "%s %s %s %s" % (self.id, self.type, self.value, self.unit)

    def get(self, sensor_id):
        self.id = sensor_id
        return self