from sensor import SmallSensor
from register_definition import REG_DAY_PROG_ECS, REG_DAY_PROG_AUX, STATE_WEEKEND, STATE_PRESENT, STATE_ABSENT, \
                            ECS_MON, ECS_TUE, ECS_WED, ECS_THU, ECS_FRI, ECS_SAT, ECS_SUN


class EcsWeekSensor(SmallSensor):

    def __init__(self, register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                 monitoring_period=None, _modbus=None, update_ihm = None):
        super().__init__(register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                         monitoring_period, _modbus, update_ihm)
        self.register_aux = REG_DAY_PROG_AUX
        self.register_ecs = REG_DAY_PROG_ECS

    def build_json_param(self, value=None):
        raise NotImplementedError('call to abstract method ' + repr(EcsWeekSensor))

    def get_cache_value(self):
        return None

    def set_sensor_value(self, value):
        list_builder = {0: self.__build_list_for_ecs_off_all_days,
                        STATE_ABSENT: self.__build_list_for_ecs_off_all_days,
                        1: self.__build_list_for_ecs_on_all_days,
                        STATE_PRESENT: self.__build_list_for_ecs_on_all_days,
                        STATE_WEEKEND: self.__build_list_for_ecs_on_weekend}

        handle_builder = list_builder.get(value, None)

        if value is None:
            raise ValueError('Bad value selected ' + repr(EcsWeekSensor))
        else:
            values_towrite = handle_builder()

        ret = self.modbus.write_area(self.register_aux, values_towrite)
        ret |= self.modbus.write_area(self.register_ecs, values_towrite)

        if not ret:
            self.__update_all_days_sensor()
        return ret

    def __update_all_days_sensor(self):
        day_list = [ECS_MON, ECS_TUE, ECS_WED, ECS_THU, ECS_FRI, ECS_SAT, ECS_SUN]
        for reg in day_list:
            sens_ecs = self.get_sensor_from_reg(reg)
            sens_ecs.update_cache_value_from_hw()

    def __build_list_for_ecs_off_all_days(self):
        list_value = []
        for day in range(7):
            list_value += [0, 0, 0]

        return list_value

    def __build_list_for_ecs_on_all_days(self):
        list_value = []
        for day in range(7):
            list_value += [0xffff, 0, 0]

        return list_value

    def __build_list_for_ecs_on_weekend(self):
        list_value = []
        for day in range(4):
            list_value += [0, 0, 0]
        for day in range(3):
            list_value += [0xffff, 0, 0]

        return list_value

    def format_extracted_json_field(self, sw_pos):
        return sw_pos
