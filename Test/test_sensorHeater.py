#!/usr/bin/env python3
from Test import register_definition, sensor_collection, extract_fields_from_json_msg
import pytest
from pytest_mock import mocker
from sensor import HeaterSensor
from sensor.derogSensor import FREEFROST_DEROG, ECO_DEROG, CONFORT_DEROG, AUTO_DEROG

IDX = 15
SVALUE1 = 20

json_heater_str = '{ \
   "Battery" : 255, \
   "LevelActions" : "|||", \
   "LevelNames" : "Off|Absent|WeekEnd|Present", \
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

STATE_ABSENT = register_definition.STATE_ABSENT
STATE_WEEKEND = register_definition.STATE_WEEKEND
STATE_PRESENT = register_definition.STATE_PRESENT


@pytest.fixture(scope="function")
def get_sensor(request):
    sensor_collection.build_sensor_collection()
    sens_col = sensor_collection.reg2sensor(register_definition.BOILER_SW_MODE)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


def test_sensor_heater_check_class_type(get_sensor):
    assert True == isinstance(get_sensor, HeaterSensor)


@pytest.mark.parametrize("level", [STATE_ABSENT, STATE_WEEKEND, STATE_PRESENT])
def test_sensor_heater_json_parameter_building_with_valid_param(get_sensor,  mocker, level):
    sensor = get_sensor
    data = level
    sensor.set_cache_value(data)
    lcl_json_str = '{"command": "switchlight", "idx": ' + str(sensor.id) + ', "switchcmd": "Set Level", "level": ' + \
                   str(data) + '}'
    json_str = sensor.build_json_param()
    assert json_str == lcl_json_str


@pytest.mark.parametrize("level", [50, 0])
def test_sensor_heater_json_parameter_building_with_unvalid_param(get_sensor, mocker, level):
    sensor = get_sensor
    data = level
    sensor.set_cache_value(data)
    json_str = sensor.build_json_param()
    assert json_str == ""


def test_sensor_heater_json_parameter_extraction(get_sensor):
    sensor = get_sensor
    sens, value = extract_fields_from_json_msg(json_heater_str)
    assert sens.id == IDX
    assert value == SVALUE1


@pytest.mark.parametrize("type, method_called", [(STATE_ABSENT, 'set_sensor2absent'),
                                                 (STATE_WEEKEND, 'set_sensor2weekend'),
                                                 (STATE_PRESENT, 'set_sensor2present')])
def test_sensor_heater_set_value_valid_parameter(get_sensor, mocker, type, method_called):
    sensor = get_sensor
    sensorFreefrost = sensor_collection.reg2sensor(register_definition.FREEFROST_DAY)
    sensorDerogB = sensor_collection.reg2sensor(register_definition.DEROGATION_CIRCUIT_B)
    sensorDerogA = sensor_collection.reg2sensor(register_definition.DEROGATION_CIRCUIT_A)
    sensorWeekEcs = sensor_collection.reg2sensor(register_definition.ECS_ALL_DAYS_IN_WEEK)
    sensorRemote = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    m = mocker.patch.object(sensorFreefrost, method_called)
    mocker.patch.object(sensorRemote, 'is_summer_mode', return_value=False)
    mocker.patch.object(sensorDerogB, 'get_derog_mode', return_value=type)
    dA = mocker.patch.object(sensorDerogA, 'set_derog_mode')
    dEcs = mocker.patch.object(sensorWeekEcs, 'set_sensor_value')
    sensor.set_sensor_value(type)
    dA.assert_called_with(type)
    dEcs.assert_called_with(type)
    m.assert_called_once_with()


def test_sensor_heater_set_value_unvalid_type(get_sensor):
    sensor = get_sensor
    with pytest.raises(ValueError):
        sensor.set_sensor_value(50)


@pytest.mark.parametrize("frost_day, cur_derog, state", [(10, FREEFROST_DEROG, STATE_ABSENT),
                                                         (4, FREEFROST_DEROG, STATE_WEEKEND),
                                                         (0, FREEFROST_DEROG, STATE_WEEKEND),
                                                         (0, AUTO_DEROG, STATE_PRESENT),
                                                         (5, AUTO_DEROG, STATE_PRESENT),
                                                         (5, CONFORT_DEROG, STATE_PRESENT),
                                                         (0, CONFORT_DEROG, STATE_PRESENT)])
def test_sensor_heater_get_sensor_value(get_sensor, mocker, frost_day, cur_derog, state):
    sensor = get_sensor
    sensorFreefrost = sensor_collection.reg2sensor(register_definition.FREEFROST_DAY)
    frost = mocker.patch.object(sensorFreefrost, 'get_cache_value', return_value=frost_day)
    sensorDerog = sensor_collection.reg2sensor(register_definition.DEROGATION_CIRCUIT_B)
    mocker.patch.object(sensorDerog, 'get_derog_mode', return_value=cur_derog)
    assert sensor.get_sensor_value() == state