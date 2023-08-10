from sensor import Sensor
import datetime

from register_definition import DEROGATION_REMOTE_1, STATE_ABSENT, STATE_WEEKEND, STATE_PRESENT, is_valid_state


class FreefrostSensor (Sensor):
    def build_json_param(self, value=None):
        if value is None:
            value = self.get_cache_value()
            if value is None:
                raise ValueError("Cache Not initialized for TempSensor id="
                                 + str(self.id) + "reg=" + str(self.register))

        # 0=gray, 1=green, 2=yellow, 3=orange, 4=red
        # if (idx == IDX_ANTIFROST_DAY):
        data = {0: 3, 1: 2, 2: 2, 3: 2, 4: 2, 5: 2}
        json_str = '{"idx": ' + str(self.id) + ', "nvalue": ' + str(data.get(value, 1))\
                   + ', "svalue": "' + str(value) + ' jours"}'
        return json_str

    def format_extracted_json_field(self, _str):
        first_space = _str.find(" ")
        return int(_str[:first_space])

    def is_freefrost_day(self, read_from_hw = 0):
        if read_from_hw:
            self.update_cache_value_from_hw()

        if self.get_cache_value() > 0:
            return True
        else:
            return False

    def set_sensor2present(self):
        self.set_sensor_value(0)

    def set_sensor_value(self, value):
        if self.get_sensor_from_reg(DEROGATION_REMOTE_1).is_summer_mode():
            return 0
        super().set_sensor_value(value)

    def set_sensor2weekend(self):
        l_weekday = [4, 3, 2, 1, 0, 0, 5]
        today = datetime.datetime.now().weekday()
        freefrost_val = l_weekday[today]

        self.set_sensor_value(freefrost_val)

    def set_sensor2absent(self, value = 90):
        self.set_sensor_value(value)

    def set_sensor_in_state(self, state):
        if not is_valid_state(state):
            raise ValueError("Bad input parameter")

        if self.get_sensor_from_reg(DEROGATION_REMOTE_1).is_summer_mode():
            return 0

        param2action = {STATE_ABSENT: self.set_sensor2absent,
                        STATE_WEEKEND: self.set_sensor2weekend,
                        STATE_PRESENT: self.set_sensor2present}

        param2action.get(state)()
