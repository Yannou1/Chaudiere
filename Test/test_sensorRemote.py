#!/usr/bin/env python3
import pytest
from Test import register_definition, sensor_collection, ModbusAccess
from pytest_mock import mocker
from sensor import RemoteSensor


@pytest.fixture(scope="function")
def get_sensor(request):
    sensor_collection.build_sensor_collection()
    sens_col = sensor_collection.reg2sensor(register_definition.DEROGATION_REMOTE_1)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


def test_sensor_remote_check_class_type(get_sensor):
    assert True == isinstance(get_sensor, RemoteSensor)


@pytest.mark.parametrize("derog_value, summer_mode", [(2, True), (18, False), (8, True), (33, True)])
def test_sensor_remote_is_winter_mode(get_sensor, mocker, derog_value, summer_mode):
    sensor = get_sensor
    m = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'read_register')
    m.return_value = derog_value
    assert summer_mode == sensor.is_summer_mode()
    assert not summer_mode == sensor.is_winter_mode()


def test_sensor_remote_set_parameter(get_sensor):
    sensor = get_sensor
    with pytest.raises(NotImplementedError):
        sensor.set_sensor_value(5)
