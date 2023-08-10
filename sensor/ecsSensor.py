from sensor import Sensor
from register_definition import  VIRTUAL_IDX, REG_DAY_DELTA_ECS_AUX


class EcsSensor(Sensor):

    def __init__(self, register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                 monitoring_period=None, _modbus=None, update_ihm=None):
        super().__init__(register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                         monitoring_period, _modbus, update_ihm)
        self.register_ecs = self.register - REG_DAY_DELTA_ECS_AUX

    def get_sensor_value(self):
        result = None
        val1 = self.modbus.read_area(self.register, 3)
        val2 = self.modbus.read_area(self.register_ecs, 3)

        if val2 is None:
            val2 = [0, 0, 0]

        if val1 is not None:
            if sum(val1) + sum(val2):
                result = 1
            else:
                result = 0

        return result

    def set_sensor_value(self, value):
        if value:
            values_towrite = [0xffff, 0, 0]
        else:
            values_towrite = [0, 0, 0]

        ret = self.modbus.write_area(self.register, values_towrite)
        ret |= self.modbus.write_area(self.register_ecs, values_towrite)

        if ret == 0:
            self.set_cache_value(value)

        return ret

    def format_extracted_json_field(self, sw_pos):
        return sw_pos

    def build_json_param(self, value=None):
        json_str = ""
        if value is None:
            value = self.get_cache_value()
            if value is None:
                raise ValueError("Cache Not initialized for TempSensor id="
                                 + str(self.id) + "reg=" + str(self.register))

        if self.id < VIRTUAL_IDX:
            json_str = self._build_json_switchcmd_str(value)
        return json_str
