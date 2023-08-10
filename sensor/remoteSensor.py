from sensor import Sensor


class RemoteSensor(Sensor):

    def build_json_param(self, value=True):
        json_str = super(RemoteSensor, self)._build_json_switchcmd_str(value)

    def format_extracted_json_field(self, _str):
        return None

    def set_sensor_value(self, value):
        raise NotImplementedError('call to abstract method ' + repr(RemoteSensor))

    def is_summer_mode(self):
        summer_bit = 0x10
        ret = False

        cache_value = self.get_cache_value()
        if cache_value is None:
            summer_derog = self.modbus.read_register(self.register, self.num_of_decimal)
            if summer_derog is not None:
                self.set_cache_value(summer_derog)
                cache_value = summer_derog
            else:
                return ret

        if not cache_value & summer_bit:
                ret = True

        return ret

    def is_winter_mode(self):
        return not self.is_summer_mode()
