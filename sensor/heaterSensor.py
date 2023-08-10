from register_definition import STATE_ABSENT, STATE_WEEKEND, STATE_PRESENT, is_valid_state, DEROGATION_CIRCUIT_A, \
                        DEROGATION_CIRCUIT_B, ECS_ALL_DAYS_IN_WEEK, FREEFROST_DAY
from sensor import Sensor
from sensor.derogSensor import DerogSensor, FREEFROST_DEROG, AUTO_DEROG
from sensor.ecsWeekSensor import EcsWeekSensor


class HeaterSensor(Sensor):
    def __init__(self, register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                 monitoring_period=None, _modbus=None,update_ihm=None):
        super().__init__(register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                         monitoring_period, _modbus, update_ihm)
        self.initialized = False
        self.sensor_derog_A = None
        self.sensor_derog_B = None
        self.sensor_ecs_week = None

    def build_json_param(self, value=None):
        json_str = ""
        if value is None:
            value = self.get_cache_value()
            if value is None:
                raise ValueError("Cache Not initialized for TempSensor id="
                                 + str(self.id) + "reg=" + str(self.register))
        if is_valid_state(value):
            json_str = self._build_json_switchlevel_str(value)

        return json_str

    def format_extracted_json_field(self, _str):
        range_value = {"10": STATE_ABSENT, "20": STATE_WEEKEND, "30": STATE_PRESENT}
        return range_value.get(_str)

    def get_sensor_value(self):
        if self.initialized is False:
            self.initialize_sensor_derog()

        if FREEFROST_DEROG == self.sensor_derog_B.get_derog_mode():
            freefrost_sens = self.get_sensor_from_reg(FREEFROST_DAY)
            if freefrost_sens.get_cache_value() > 5:
                state = STATE_ABSENT
            else:
                state = STATE_WEEKEND
        else:
            state = STATE_PRESENT

        return state

    def set_sensor_value(self, state):
        if not is_valid_state(state):
            raise ValueError("Bad input parameter")

        if self.initialized is False:
            self.initialize_sensor_derog()

        self.sensor_derog_B.set_sensor_in_state(state)
        current_derog_circuitB = self.sensor_derog_B.get_derog_mode()
        self.sensor_derog_A.set_derog_mode(current_derog_circuitB)
        self.sensor_ecs_week.set_sensor_value(state)
        self.set_cache_value(state)

    def initialize_sensor_derog(self):
        if self.initialized is False:
            self.sensor_derog_A = self.get_sensor_from_reg(DEROGATION_CIRCUIT_A)
            if not isinstance(self.sensor_derog_A, DerogSensor):
                raise TypeError("second parameter is not DerogSensor object")

            self.sensor_derog_B = self.get_sensor_from_reg(DEROGATION_CIRCUIT_B)
            if not isinstance(self.sensor_derog_B, DerogSensor):
                raise TypeError("second parameter is not DerogSensor object")

            self.sensor_ecs_week = self.get_sensor_from_reg(ECS_ALL_DAYS_IN_WEEK)
            if not isinstance(self.sensor_ecs_week, EcsWeekSensor):
                print(self.sensor_ecs_week)
                print(EcsWeekSensor)
                raise TypeError("second parameter is not EcsWeekSensor object")

            self.initialized = True
