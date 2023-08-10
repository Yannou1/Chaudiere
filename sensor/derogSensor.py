from sensor import Sensor
from register_definition import DEROGATION_REMOTE_1, FREEFROST_DAY, DEROGATION_CIRCUIT_B
from prj_logger import logging
from register_definition import STATE_ABSENT, STATE_WEEKEND, STATE_PRESENT, is_valid_state
from sensor.freefrostSensor import FreefrostSensor
from time import sleep

sensor_error = -1

NO_DEROG            = 0
FREEFROST_DEROG     = 1
ECO_DEROG           = 2
CONFORT_DEROG       = 4
AUTO_DEROG          = 8
ECS_DEROG           = 0x10
PERM_DEROG          = 0x20
SUMMER_DEROG        = 0x10
RESET_DEROG         = 0xFFC0
HEATER_DEROG_FLAG   = 0xF
RESET_SUMMER_DEROG  = 0xFFEF
UNKNOWN_DEROG       = None

derog_list_values = [FREEFROST_DEROG, ECO_DEROG, CONFORT_DEROG, AUTO_DEROG]

class DerogSensor (Sensor):

    def __init__(self, register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                 monitoring_period=None, _modbus=None,update_ihm=None):
        super().__init__(register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                         monitoring_period, _modbus, update_ihm)
        self.initialized = False
        self.sensor_freefrost = None

    def build_json_param(self, value=None):
        result = None
        json_str = ""
        if value is None:
            value = self.get_cache_value()
            if value is None:
                raise ValueError("Cache Not initialized for TempSensor id="
                                 + str(self.id) + "reg=" + str(self.register))

        for i in range(0, 5):
            if ((value >> i) & 0x1) == 1:
                result = ((i + 1) * 10)
                break

        if result is not None:
            json_str = super(DerogSensor, self)._build_json_switchlevel_str(result)

        return json_str

    def format_extracted_json_field(self, _str):
        try:
            value = int(int(_str)/10) - 1
            return derog_list_values[value]
        except IndexError:
            return None

    def get_derog_mode_from_raw(self, derog_raw):
        for bit_val in derog_list_values:
            if derog_raw & bit_val:
                return bit_val

        return UNKNOWN_DEROG

    def get_derog_mode(self):
        derog_raw = self.get_sensor_value()
        return self.get_derog_mode_from_raw(derog_raw)

    def set_derog_mode(self, value):
        self.set_sensor_value(value)

    def __is_summer_mode(self):
        return self.get_sensor_from_reg(DEROGATION_REMOTE_1).is_summer_mode()

    def __validate_derogation_mode(self, value):
        try:
            derog_list_values.index(value)
            return 0
        except ValueError:
            logging.error("derogation value error \"%s\"" % value)
            return sensor_error

    def set_sensor_value(self, value):
        if sensor_error == self.__validate_derogation_mode(value):
            return sensor_error

        if self.__is_summer_mode():
            return 0

        sens_val = self.get_sensor_value()
        if (sens_val & HEATER_DEROG_FLAG) != value:
            val_to_write = (sens_val & RESET_DEROG) | value
            ret = super().set_sensor_value(val_to_write)
        else:
            logging.debug("derogation already set to the current value \"%s\"" % value)
            ret = 0
        return ret

    def __set_sensor2present(self):
        self.sensor_freefrost.set_sensor2present()
        sleep(0.2)
        if self.get_derog_mode == FREEFROST_DEROG:
            self.set_sensor_value(AUTO_DEROG)

    def set_sensor_in_state(self, state):
        self.__initialize_sensor()

        if not is_valid_state(state):
            raise ValueError("Bad input parameter")

        if self.__is_summer_mode():
            return 0

        if DEROGATION_CIRCUIT_B == self.register:
            param2action = {STATE_ABSENT: self.sensor_freefrost.set_sensor2absent,
                            STATE_WEEKEND: self.sensor_freefrost.set_sensor2weekend,
                            STATE_PRESENT: self.__set_sensor2present}
            param2action.get(state)()
        else:
            self.set_sensor_value(state)



    def __initialize_sensor(self):
        if self.initialized is False:
            self.sensor_freefrost = self.get_sensor_from_reg(FREEFROST_DAY)
            if not isinstance(self.sensor_freefrost, FreefrostSensor):
                raise TypeError("second parameter is not DerogSensor object")

            self.initialized = True


