from sensor import Sensor
NEGATIVE_VALUE_POINT = 32768


class TempSensor(Sensor):
    def __init__(self, register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                 monitoring_period=None, _modbus=None, update_ihm=None):
        super().__init__(register, _id, sensor_type, get_sensor_from_reg, get_sensor_from_idx,
                         monitoring_period, _modbus, update_ihm)
        self.num_of_decimal = 1
        self.write_enable = False

    def build_json_param(self, value=None):
        if value is None:
            value = self.get_cache_value()
            if value is None:
                raise ValueError("Cache Not initialized for TempSensor id="
                                    + str(self.id) + "reg=" + str(self.register))

        json_str = self._build_json_temp_setpoint_str(value)
        return json_str

    def format_extracted_json_field(self, _str):
        return None

    def get_sensor_value(self):
        value = super().get_sensor_value()
        if value is not None:
            value = self.format_for_negative_value(value)

        return value

    def format_for_negative_value(self, value):
        """
        Return the value fromatted for negative value if required
        :param reg: register for which the value will be returned
        :param value: value to br formatted
        :return: 0 or 1
        """
        if self.num_of_decimal:
            negative_point = NEGATIVE_VALUE_POINT / 10
        else:
            negative_point = NEGATIVE_VALUE_POINT

        if value > negative_point:
            value = round(float(negative_point - value), 1)

        return value
