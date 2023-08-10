#!/usr/bin/env python3
import pytest

from Test import register_definition, sensor_collection
from sensor import TempSensor

#https://stackoverflow.com/questions/44166134/pytest-with-mock-pytest-mock

IDX = 3
SVALUE1 = 23

TEMPERATURE_NEG = -10
TEMPERATURE_POS = 10
DECIMAL = 10
NEGATIVE_VALUE_POINT = (0x10000 / 2)/10

json_temperature_str = '{ \
   "dtype" : "Temp", \
   "id" : "82002", \
   "idx" : ' + str(IDX) + ', \
   "name" : "Outside_temp", \
   "nvalue" : ' + str(IDX) + ', \
   "stype" : "THR128/138, THC138", \
   "svalue1" : "' + str(SVALUE1) + '", \
   "unit" : 1 \
}'

@pytest.fixture(scope="function")
def get_sensor(request):
    sensor_collection.build_sensor_collection()
    sens_col = sensor_collection.reg2sensor(register_definition.TEMP_AMBIANT_CIRCUIT_B)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col

@pytest.fixture(scope="function")
def mock_modbus_read(mocker, get_sensor):
    m = mocker.patch.object(get_sensor, 'modbus')
    return mocker.patch.object(m, 'read_register')

def test_sensor_temp_json_parameter_exception(get_sensor):
    with pytest.raises(ValueError):
        get_sensor.build_json_param()


def test_sensor_temp_check_class_type(get_sensor):
    assert True == isinstance(get_sensor, TempSensor)


def test_sensor_temp_json_parameter_building(get_sensor):
    sensor = get_sensor
    data = 10
    sensor.set_cache_value(data)
    lcl_json_str = '{"idx": ' + str(sensor.id) + ', "svalue": "' + str(sensor.get_cache_value()) + '"}'
    json_str = sensor.build_json_param()

    assert json_str == lcl_json_str


def test_sensor_temp_json_parameter_extraction(get_sensor):
    from util import extract_fields_from_json_msg
    sens, value = extract_fields_from_json_msg(json_temperature_str)
    assert sens == None
    assert value == None


def test_sensor_temp_check_negative_value(get_sensor):
    sensor = get_sensor
    assert sensor.format_for_negative_value(NEGATIVE_VALUE_POINT - TEMPERATURE_NEG) == TEMPERATURE_NEG
    assert sensor.format_for_negative_value(TEMPERATURE_POS) == TEMPERATURE_POS


def test_sensor_temp_check_num_of_dec(get_sensor):
    sensor = get_sensor
    assert sensor.num_of_decimal == 1


@pytest.mark.parametrize("ret_val", [20.0, 18.5])
def test_sensor_temp_get_positive_value(get_sensor, mock_modbus_read, ret_val):
    sensor = get_sensor
    mock = mock_modbus_read
    mock.return_value=ret_val
    sensor.get_sensor_value()
    assert sensor.get_sensor_value() == ret_val



def test_sensor_temp_get_negative_value(get_sensor, mock_modbus_read):
    sensor = get_sensor
    mock = mock_modbus_read
    NEG_VALUE=-35
    mock.return_value=NEGATIVE_VALUE_POINT - NEG_VALUE
    assert sensor.get_sensor_value() == NEG_VALUE
