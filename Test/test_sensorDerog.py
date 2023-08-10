#!/usr/bin/env python3
import pytest
from Test import register_definition, sensor_collection
from sensor.derogSensor import NO_DEROG, FREEFROST_DEROG, ECO_DEROG, CONFORT_DEROG, AUTO_DEROG, UNKNOWN_DEROG, RESET_DEROG
from pytest_mock import mocker
from sensor import DerogSensor

@pytest.fixture(scope="function")
def get_sensor(request):
    sensor_collection.build_sensor_collection()
    sens_col = sensor_collection.reg2sensor(register_definition.DEROGATION_CIRCUIT_A)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


def test_sensor_derog_check_class_type(get_sensor):
    assert True == isinstance(get_sensor, DerogSensor)


@pytest.mark.parametrize("value, str_type", [(0,None), (1, not None), (2, not None), (3, not None),
                                             (4, not None), (5, not None), (6, None)])
def test_sensor_derog_json_parameter_building(get_sensor, value, str_type):
    sensor = get_sensor
    level = 10
    sensor.set_cache_value(level)
    if str_type is None:
        lcl_json_str = ""
    else:
        lcl_json_str = '{"command": "switchlight", "idx": ' + str(sensor.id) + ', "switchcmd": "Set Level", "level": ' + str(level) + '}'
    json_str = sensor.build_json_param()


@pytest.mark.parametrize("derog_value, ret_derog", [(0, UNKNOWN_DEROG), (1, FREEFROST_DEROG), (2, ECO_DEROG),
                                                    (0, UNKNOWN_DEROG), (4, CONFORT_DEROG), (8, AUTO_DEROG),
                                                    (16, UNKNOWN_DEROG)])
def test_sensor_derog_check_derog_mode(get_sensor, derog_value, ret_derog):
    sensor = get_sensor
    assert ret_derog == sensor.get_derog_mode_from_raw(derog_value)


@pytest.mark.parametrize("cur_derog, derog, return_val", [(AUTO_DEROG+32, FREEFROST_DEROG, 0),
                                                          (CONFORT_DEROG, ECO_DEROG, 0),
                                                          (ECO_DEROG, CONFORT_DEROG, 0),
                                                          (CONFORT_DEROG, AUTO_DEROG, 0)])
def test_sensor_derog_set_derog_mode_valid_value(get_sensor, mocker, cur_derog, derog, return_val):
    sensor = get_sensor
    sensorRemote = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    mocker.patch.object(sensorRemote, 'is_summer_mode', return_value=False)
    mocker.patch.object(sensor, 'get_sensor_value', return_value=cur_derog)
    mw = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'write_register')
    mw.return_value = return_val
    val_to_write = (cur_derog & RESET_DEROG) | derog
    assert return_val == sensor.set_sensor_value(derog)
    mw.assert_called_with(sensor.register, val_to_write, sensor.num_of_decimal)


@pytest.mark.parametrize("cur_derog, derog, return_val", [(FREEFROST_DEROG, 0, -1), (AUTO_DEROG, 32, -1)])
def test_sensor_derog_set_derog_mode_unvalid_value(get_sensor, mocker, cur_derog, derog, return_val):
    sensor = get_sensor
    mocker.patch.object(sensor, 'get_sensor_value', return_value=cur_derog)
    mw = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'write_register')
    mw.assert_not_called()
    assert return_val == sensor.set_sensor_value(derog)


def test_sensor_derog_set_derog_mode_same_value(get_sensor, mocker):
    sensor = get_sensor
    sensorRemote = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    mocker.patch.object(sensorRemote, 'is_summer_mode', return_value=False)
    mocker.patch.object(sensor, 'get_sensor_value', return_value=FREEFROST_DEROG+32)
    mw = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'write_register')
    mw.assert_not_called()
    assert 0 == sensor.set_sensor_value(FREEFROST_DEROG)

@pytest.mark.parametrize("derog", [FREEFROST_DEROG, AUTO_DEROG, ECO_DEROG, CONFORT_DEROG])
def test_sensor_derog_set_derog_mode_in_summer_mode(get_sensor, mocker, derog):
    sensor = get_sensor
    sensorRemote = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    mocker.patch.object(sensorRemote, 'is_summer_mode', return_value=True)
    m_object = mocker.patch.object(sensor, 'get_sensor_value')
    sensor.set_sensor_value(FREEFROST_DEROG)
    m_object.assert_not_called()


