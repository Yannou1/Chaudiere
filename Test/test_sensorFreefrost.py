#!/usr/bin/env python3
import pytest
from Test import register_definition, sensor_collection, ModbusAccess
from pytest_mock import mocker
from sensor import FreefrostSensor
import datetime

IDX = 1
SVALUE1 = 23


@pytest.fixture(scope="function")
def get_sensor(request):
    sensor_collection.build_sensor_collection()
    sens_col = sensor_collection.reg2sensor(register_definition.FREEFROST_DAY)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


def test_sensor_freefrost_json_parameter_exception(get_sensor):
    with pytest.raises(ValueError):
        get_sensor.build_json_param()


def test_sensor_freefrost_check_class_type(get_sensor):
    assert True == isinstance(get_sensor, FreefrostSensor)


@pytest.mark.parametrize("value, alert", [(0,3), (80,1), (1,2), (2,2), (3,2), (4,2), (5,2), (99,1)])
def test_sensor_freefrost_json_parameter_building(get_sensor, value, alert):
    sensor = get_sensor
    sensor.set_cache_value(value)
    lcl_json_str = '{"idx": ' + str(sensor.id) + ', "nvalue": ' + str(alert) + ', "svalue": "' + str(value) + ' jours"}'
    json_str = sensor.build_json_param()
    assert json_str == lcl_json_str


def test_sensor_freefrost_get_sensor_value(get_sensor, mocker):
    sensor = get_sensor
    read_value = 5
    m = mocker.patch.object(sensor, 'get_sensor_value', return_value=read_value)
    assert sensor.get_sensor_value() == read_value

@pytest.mark.parametrize("state", [register_definition.STATE_WEEKEND])
def test_sensor_freefrost_set_sensor_value_we_winter_mode(get_sensor, mocker, state):
    sensor = get_sensor
    l_weekday = [4, 3, 2, 1, 0, 0, 5]
    sensorRemote = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    mocker.patch.object(sensorRemote, 'is_summer_mode', return_value=False)
    m_object = mocker.patch.object(sensor, 'set_sensor_value')
    sensor.set_sensor_in_state(state)
    m_object.assert_called_with(l_weekday[datetime.datetime.now().weekday()])


@pytest.mark.parametrize("state, nbr_days", [(register_definition.STATE_ABSENT, 90),
                                             (register_definition.STATE_PRESENT, 0)])
def test_sensor_freefrost_set_sensor_value_winter_mode(get_sensor, mocker, state, nbr_days):
    sensor = get_sensor
    sensorRemote = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    mocker.patch.object(sensorRemote, 'is_summer_mode', return_value=False)
    m_object = mocker.patch.object(sensor, 'set_sensor_value')
    sensor.set_sensor_in_state(state)
    m_object.assert_called_with(nbr_days)


@pytest.mark.parametrize("state", [register_definition.STATE_ABSENT, register_definition.STATE_PRESENT,
                                    register_definition.STATE_WEEKEND])
def test_sensor_freefrost_set_sensor_value_summer_mode(get_sensor, mocker, state):
    sensor = get_sensor
    sensorRemote = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    mocker.patch.object(sensorRemote, 'is_summer_mode', return_value=True)
    m_object = mocker.patch.object(sensor, 'set_sensor_value')
    sensor.set_sensor_in_state(state)
    m_object.assert_not_called()

def test_sensor_freefrost_set_sensor_value_summer_mode(get_sensor, mocker):
    sensor = get_sensor
    sensorRemote = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    mw = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'write_register')
    mocker.patch.object(sensorRemote, 'is_summer_mode', return_value=True)
    sensor.set_sensor_in_state(register_definition.STATE_ABSENT)
    mw.assert_not_called()

def test_sensor_freefrost_set_sensor_value_winter_mode(get_sensor, mocker):
    sensor = get_sensor
    sensorRemote = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    mw = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'write_register')
    mocker.patch.object(sensorRemote, 'is_summer_mode', return_value=False)
    sensor.set_sensor_in_state(register_definition.STATE_ABSENT)
    mw.assert_called_with(sensor.register, 90, 0)