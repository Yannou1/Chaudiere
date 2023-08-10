#!/usr/bin/env python3
import pytest
from Test import sensor_collection, register_definition

TEMP_ID = 11
PROG_ID = 3
TEMP_REG = 102
PROG_REG = 1000

TEMP_PERIOD = 30
PROG_PERIOD = 20

reg_definition = (
    (TEMP_ID, TEMP_REG, register_definition.TYPE_TEMPERATURE, register_definition.MONITORED, TEMP_PERIOD, []),
    (PROG_ID, PROG_REG, register_definition.TYPE_PROG, register_definition.MONITORED, PROG_PERIOD, [])
)


@pytest.fixture(scope="function")
def get_sensor_collection(request):
    sens_col = sensor_collection.build_sensor_collection(reg_definition)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


def test_sensor_do_not_overwrite_collection(get_sensor_collection):
    other_reg = 50
    reg_definition_tmp = (
        (other_reg, TEMP_REG, register_definition.TYPE_TEMPERATURE, register_definition.MONITORED, TEMP_PERIOD, []),
    )
    sens_col = get_sensor_collection
    other_sens = sensor_collection.build_sensor_collection(reg_definition_tmp)
    sensor = sensor_collection.reg2sensor(TEMP_REG)
    assert sensor.register == TEMP_REG
    assert sens_col == other_sens
    assert (sensor_collection.reg2sensor(TEMP_REG)).register == TEMP_REG


def test_sensor_get_from_collection():
    sensor = sensor_collection.reg2sensor(TEMP_REG)
    sensor_id = sensor_collection.id2sensor(TEMP_ID)
    assert sensor == sensor_id


def test_sensor_check_content(get_sensor_collection):
    sensor1 = sensor_collection.reg2sensor(TEMP_REG)
    sensor2 = sensor_collection.id2sensor(PROG_ID)

    assert sensor1.register == TEMP_REG
    assert sensor1.id == TEMP_ID
    assert sensor1.sensor_type == register_definition.TYPE_TEMPERATURE
    assert sensor1.monitoring_period == TEMP_PERIOD
    assert sensor2.register == PROG_REG
    assert sensor2.id == PROG_ID
    assert sensor2.sensor_type == register_definition.TYPE_PROG
    assert sensor2.monitoring_period == PROG_PERIOD


def test_sensor_build_full_collection():
    sens_col = sensor_collection.build_sensor_collection()
    assert len(sens_col) == len(register_definition.get_system_config()) - sensor_collection.get_number_of_virtual_sensor()
