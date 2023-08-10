from sensor import Sensor

sensor_error = -1
range_value = [10, 20, 30, 40]
class ProgSensor(Sensor):
    def build_json_param(self, value=None):
        result = None
        json_str = ""
        if value is None:
            value = self.get_cache_value()
            if value is None:
                raise ValueError("Cache Not initialized for TempSensor id="
                                 + str(self.id) + "reg=" + str(self.register))

        try:
            value = range_value[value]
            json_str = self._build_json_switchlevel_str(value)
        except IndexError:
            json_str = ""

        return json_str

    def format_extracted_json_field(self, _str):
        try:
            value = range_value.index(int(_str))
        except ValueError:
            value = None

        return value


    def set_sensor_value(self, value):
        if value < 0 and value > 3:
            return sensor_error

        return super().set_sensor_value(value)


