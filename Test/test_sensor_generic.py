#!/usr/bin/env python3
import pytest
import time
from Test import sensor_collection, register_definition
from sensor import TempSensor, DerogSensor
from pytest_mock import mocker

@pytest.fixture(scope="function")
def get_sensor(request):
    sensor_collection.build_sensor_collection()
    sens_col = sensor_collection.reg2sensor(register_definition.FREEFROST_DAY)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


def test_sensor_generic_scheduler(get_sensor, mocker):
    sensor = get_sensor
    sensor.set_next_time2monitor(1)
    mocker.spy(sensor, 'update_cache_value_from_hw')
    mocker.patch.object(sensor, 'update_cache_value_from_hw', return_value=None)
    sensor.is_time2monitor()
    assert sensor.update_cache_value_from_hw.call_count == 0
    time.sleep(1)
    sensor.is_time2monitor()
    assert sensor.update_cache_value_from_hw.call_count == 1


def test_sensor_generic_check_cache_data(get_sensor):
    sensor = get_sensor
    data = 10
    sensor.set_cache_value(data)
    assert sensor.get_cache_value() == data

def test_sensor_get_sensor_from_class(get_sensor):
    sensor = get_sensor
    sensor2 = sensor.get_sensor_from_reg(register_definition.DEROGATION_CIRCUIT_A)
    assert True == isinstance(sensor2, DerogSensor)
    sensor3 = sensor.get_sensor_from_idx(5)
    assert True == isinstance(sensor3, TempSensor)

def test_sensor_generic_autoscheduling(get_sensor, mocker):
    sensor = get_sensor
    sensor.monitoring_period = 1
    sensor.set_next_time2monitor()
    mocker.spy(sensor, 'update_cache_value_from_hw')
    mocker.patch.object(sensor, 'update_cache_value_from_hw')
    sensor.is_time2monitor()
    assert sensor.update_cache_value_from_hw.call_count == 0
    time.sleep(1)
    sensor.is_time2monitor()
    assert sensor.update_cache_value_from_hw.call_count == 1


def test_sensor_generic_update_cache_after_read(get_sensor, mocker):
    reg_value = 25
    sensor = get_sensor
    sensor.set_cache_value(None)
    m = mocker.patch.object(sensor, 'modbus')
    mock_read = mocker.patch.object(m, 'read_register')
    mock_read.return_value = reg_value
    mocker.spy(sensor, 'set_cache_value')
    mocker.spy(sensor, 'ihm_update_sensor')
    sensor.update_cache_value_from_hw()
    assert sensor.set_cache_value.call_count == 1
    assert sensor.ihm_update_sensor.call_count == 1
