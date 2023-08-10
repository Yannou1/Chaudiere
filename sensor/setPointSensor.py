from register_definition import TEMP_SETPOINT_CONFORT_A, TEMP_SETPOINT_ECO_A, TEMP_SETPOINT_FREEFROST_A, \
                                    TEMP_SETPOINT_CONFORT_B, TEMP_SETPOINT_ECO_B, TEMP_SETPOINT_FREEFROST_B, \
                                    TEMP_SETPOINT_ECS
from .tempSensor import TempSensor
from prj_logger import logging

sensor_error = -1

sensor_sub_type = {
    TEMP_SETPOINT_CONFORT_A: "confort",
    TEMP_SETPOINT_ECO_A: "eco",
    TEMP_SETPOINT_FREEFROST_A: "freefrost",
    TEMP_SETPOINT_CONFORT_B: "confort",
    TEMP_SETPOINT_ECO_B: "eco",
    TEMP_SETPOINT_FREEFROST_B: "freefrost",
    TEMP_SETPOINT_ECS: "ecs"
}

temp_range = {
    "confort": {"min": 14, "max": 24},
    "eco": {"min": 12, "max": 20},
    "freefrost": {"min": 0.5, "max": 16},
    "ecs": {"min": 50, "max": 80},
    "default": {"min": 15, "max": 20}
}


class SetPointSensor (TempSensor):

    def __init__(self, register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                 monitoring_period=None, _modbus=None, update_ihm=None):
        super().__init__(register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                         monitoring_period, _modbus, update_ihm)
        self.num_of_decimal = 1
        self.write_enable = True
        temp_type = temp_range.get(sensor_sub_type.get(register, "default"))
        self.temp_min = temp_type.get("min")
        self.temp_max = temp_type.get("max")

    def build_json_param(self, value=None):
        if value is None:
            value = self.get_cache_value()
            if value is None:
                raise ValueError("Cache Not initialized for TempSensor id="
                                 + str(self.id) + "reg=" + str(self.register))

        json_str = self._build_json_temp_setpoint_str(value)
        return json_str

    @staticmethod
    def __round_value(value):
        return (round(value*2))/2

    def set_sensor_value(self, value):
        cur_value = (self.__round_value(value) * 1.0)
        if (cur_value >= self.temp_min) and (cur_value <= self.temp_max):
            return super().set_sensor_value(cur_value)
        else:
            logging.error("Value %d is out of range[%d, %d]" % (cur_value, self.temp_min, self.temp_max))
            return sensor_error

    def format_extracted_json_field(self, _str):
        from util import string2float
        return string2float(_str)