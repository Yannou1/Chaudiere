#!/usr/bin/env python3
import pytest

from Test import register_definition, sensor_collection
from sensor import EcsSensor

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
    sens_col = sensor_collection.reg2sensor(register_definition.ECS_MON)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


def test_sensor_ecs_check_class_type(get_sensor):
    assert True == isinstance(get_sensor, EcsSensor)


def test_sensor_ecs_json_parameter_exception(get_sensor):
    with pytest.raises(ValueError):
        get_sensor.build_json_param()


@pytest.mark.parametrize("state, state_str", [(1, "On"), (0, "Off")])
def test_sensor_ecs_json_parameter_building_on_value(get_sensor, state, state_str):
    sensor = get_sensor
    sensor.set_cache_value(state)
    lcl_json_str = '{"command": "switchlight", "idx": ' + str(sensor.id) + ', "switchcmd": "' + state_str + '"}'
    json_str = sensor.build_json_param()
    assert json_str == lcl_json_str


def test_sensor_ecs_json_parameter_extraction(get_sensor):
    from util import extract_fields_from_json_msg
    sens, value = extract_fields_from_json_msg(json_ecs_str)
    assert sens.id == IDX
    assert value == NVALUE


@pytest.mark.parametrize("value, ret", [([10, 0, 0], True), ([0, 0, 0], False), ([0, 4, 0], True)])
def test_sensor_ecs_read_ecs_config(get_sensor, mocker, value, ret):
    sensor = get_sensor
    m = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'read_area')
    m.return_value = value
    assert ret == sensor.get_sensor_value()
    assert m.call_count == 2


@pytest.mark.parametrize("ecs_conf, cache_value", [([10, 0, 0], 1), ([0, 0, 0], 0), ([0, 4, 0], 1)])
def test_sensor_ecs_check_cache_value_stored(get_sensor, mocker, ecs_conf, cache_value):
    sensor = get_sensor
    m = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'read_area')
    m.return_value = ecs_conf
    sensor.update_cache_value_from_hw()
    assert cache_value == sensor.get_cache_value()
    assert m.call_count == 2


@pytest.mark.parametrize("value, param", [(True, [0xffff, 0, 0]), (2, [0xffff, 0, 0]), (False, [0, 0, 0]),
                                          (0, [0, 0, 0])])
def test_sensor_ecs_write_ecs_config(get_sensor, mocker, value, param):
    sensor = get_sensor
    m = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'write_area')
    sensor.set_sensor_value(value)
    m.assert_called_with(sensor.register_ecs, param)
    assert m.call_count == 2
