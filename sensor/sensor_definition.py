import time
from prj_logger import logging

class Sensor(object):
    def __init__(self, register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                 monitoring_period=None, _modbus=None, update_ihm=None):
        self.modbus = _modbus
        self.register = register
        self.write_enable = True
        self.id = _id
        self.ihm_need_update = False
        self.sensor_type = sensor_type
        self.monitoring_period = monitoring_period if monitoring_period is not None else 0xffffffff
        self.time_delay = None
        self.cache_register = None
        self.num_of_decimal = 0
        self.update_ihm = update_ihm
        self.get_sensor_from_reg = get_sensor_from_reg
        self.get_sensor_from_idx = get_sensor_from_idx

    def send_json_param(self):
        if self.update_ihm is not None:
            json_str = self.build_json_param(self.get_cache_value())
            self.update_ihm(json_str, self.id, self.get_cache_value())

    def _build_json_temp_setpoint_str(self, value):
        json_str = '{"idx": ' + str(self.id) + ', "svalue": "' + str(value) + '"}'
        return json_str

    def __build_json_switch_prefix_str(self):
        json_str = '{"command": "switchlight", "idx": ' + str(self.id)
        return json_str

    def _build_json_switchlevel_str(self, level):
        prefix = self.__build_json_switch_prefix_str()
        suffix = ', "switchcmd": "Set Level", "level": ' + str(level) + '}'
        return prefix + suffix

    def _build_json_switchcmd_str(self, sw_pos):
        if sw_pos:
            str_value = "On"
        else:
            str_value = "Off"
        prefix = self.__build_json_switch_prefix_str()
        suffix = ', "switchcmd": "' + str_value + '"}'
        return prefix + suffix

    def build_json_param(self, value=None):
        raise NotImplementedError('call to abstract method ' + repr(Sensor))

    def format_extracted_json_field(self, _str):
        raise NotImplementedError('call to abstract method ' + repr(Sensor))

    def get_sensor_value(self):
        return self.modbus.read_register(self.register, self.num_of_decimal)

    def set_sensor_value(self, value):
        ret = self.modbus.write_register(self.register, value, self.num_of_decimal)
        if not ret:
            self.update_cache_value_from_hw()

        return ret

    def update_cache_value_from_hw(self):
        value = self.get_sensor_value()

        if value is not None:
            if value != self.get_cache_value():
                self.set_cache_value(value)
                self.ihm_update_sensor()
                logging.debug("************ domoticz sensor(%d) need to be updated ************" % self.id)

    def get_cache_value(self):
        return self.cache_register

    def set_cache_value(self, cache_value):
        self.cache_register = cache_value

    def set_next_time2monitor(self, next_time=None):
        if next_time is not None:
            self.time_delay = time.time() + next_time
            return
        if self.monitoring_period is not None:
            self.time_delay = time.time() + self.monitoring_period

    def get_next_time2monitor(self):
        return self.time_delay

    def is_time2monitor(self):
        n_time = self.get_next_time2monitor()
        if n_time is not None:
            remaining_time = n_time - time.time()
        else:
            remaining_time = -1

        if remaining_time < 0:
            logging.debug("Yeah... It's time to read for updating cache id %d" % self.id)
            self.update_cache_value_from_hw()
            self.set_next_time2monitor()


    def ihm_update_sensor(self):
        if self.update_ihm is not None:
            self.send_json_param()