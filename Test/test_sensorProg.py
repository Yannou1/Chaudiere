#!/usr/bin/env python3
import pytest

from Test import register_definition, sensor_collection, extract_fields_from_json_msg
from sensor import ProgSensor

IDX = 100
SVALUE1 = 20

json_prog_str = '{ \
   "Battery" : 255, \
   "LevelActions" : "|||", \
   "LevelNames" : "P1|P2|P3|P4", \
   "LevelOffHidden" : "true", \
   "RSSI" : 12, \
   "SelectorStyle" : "0", \
   "description" : "Boiler Management", \
   "dtype" : "Light/Switch", \
   "id" : "0001405E", \
   "idx" : ' + str(IDX) + ', \
   "name" : "Boiler Mode", \
   "nvalue" : 2, \
   "stype" : "Selector Switch", \
   "svalue1" : "' + str(SVALUE1) + '", \
   "switchType" : "Selector", \
   "unit" : 1 \
}'

@pytest.fixture(scope="function")
def get_sensor(request):
    sensor_collection.build_sensor_collection()
    sens_col = sensor_collection.reg2sensor(register_definition.PROG_NUM_A)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


def test_sensor_prog_check_class_type(get_sensor):
    assert True == isinstance(get_sensor, ProgSensor)

def test_sensor_prog_json_parameter_extraction(get_sensor):
    sensor = get_sensor
    sens, value = extract_fields_from_json_msg(json_prog_str)
    assert sens.id == IDX
    assert value == (SVALUE1/10) - 1

@pytest.mark.parametrize("level", [0, 3, 2, 1])
def test_sensor_prog_json_parameter_building_with_valid_param(get_sensor,  mocker, level):
    sensor = get_sensor
    data = (level+1)*10
    sensor.set_cache_value(level)
    lcl_json_str = '{"command": "switchlight", "idx": ' + str(sensor.id) + ', "switchcmd": "Set Level", "level": ' + \
                   str(data) + '}'
    json_str = sensor.build_json_param()
    assert json_str == lcl_json_str


@pytest.mark.parametrize("level", [5, 10])
def test_sensor_prog_json_parameter_building_with_unvalid_param(get_sensor, mocker, level):
    sensor = get_sensor
    data = (level+1)*10
    sensor.set_cache_value(level)
    json_str = sensor.build_json_param()
    assert json_str == ""