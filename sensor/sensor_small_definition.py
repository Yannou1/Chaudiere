import time


class SmallSensor(object):
    def __init__(self, register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                 monitoring_period=None, _modbus=None, update_ihm=None):
        self.modbus = _modbus
        self.register = register
        self.id = _id
        self.write_enable = True
        self.sensor_type = sensor_type
        self.monitoring_period = monitoring_period
        self.num_of_decimal = 0
        self.update_ihm = None
        self.get_sensor_from_reg = get_sensor_from_reg
        self.get_sensor_from_idx = get_sensor_from_idx

    def format_extracted_json_field(self, _str):
        raise NotImplementedError('call to abstract method ' + repr(SmallSensor))

    def get_sensor_value(self, value):
        raise NotImplementedError('call to abstract method ' + repr(SmallSensor))

    def set_sensor_value(self, value):
        raise NotImplementedError('call to abstract method ' + repr(SmallSensor))

    def is_time2monitor(self):
        pass

