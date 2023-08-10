#!/usr/bin/env python3
import pytest

from Test import register_definition, sensor_collection
from sensor import EcsWeekSensor

STATE_PRESENT = register_definition.STATE_PRESENT
STATE_ABSENT = register_definition.STATE_ABSENT
STATE_WEEKEND = register_definition.STATE_WEEKEND

IDX = 22
NVALUE = 0

json_ecs_str = '{ \
   "Battery" : 255, \
   "RSSI" : 12, \
   "description" : "", \
   "dtype" : "Light/Switch", \
   "id" : "00014066", \
   "idx" : ' + str(IDX) + ' , \
   "name" : "ECS Lun", \
   "nvalue" : 0, \
   "stype" : "Switch", \
   "svalue1" : "' + str(NVALUE) + '", \
   "switchType" : "On/Off", \
   "unit" : 1  }'


@pytest.fixture(scope="function")
def get_sensor(request):
    sensor_collection.build_sensor_collection()
    sens_col = sensor_collection.reg2sensor(register_definition.ECS_ALL_DAYS_IN_WEEK)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


def test_sensor_ecs_week__check_class_type(get_sensor):
    assert True == isinstance(get_sensor, EcsWeekSensor)

def test_sensor_ecs_week_json_parameter_extraction(get_sensor):
    from util import extract_fields_from_json_msg
    sens, value = extract_fields_from_json_msg(json_ecs_str)
    assert sens.id == IDX
    assert value == NVALUE


@pytest.mark.parametrize("switch, listOfValues",
                         [(STATE_PRESENT, [0xffff, 0, 0, 0xffff, 0, 0, 0xffff, 0, 0, 0xffff, 0, 0, 0xffff, 0, 0, 0xffff, 0, 0,
                                           0xffff, 0, 0]),
                          (STATE_ABSENT, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
                          (STATE_WEEKEND, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xffff, 0, 0, 0xffff, 0, 0, 0xffff, 0, 0])])
def test_sensor_ecs_week_write_ecs_config(get_sensor, mocker, switch, listOfValues):
    sensor = get_sensor
    m = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'write_area')
    sensor.set_sensor_value(switch)
    m.assert_called_with(sensor.register_ecs, listOfValues)
    assert m.call_count == 2

