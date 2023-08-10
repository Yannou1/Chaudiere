from Test import register_definition, sensor_collection
from util import extract_fields_from_json_msg
import pytest
from sensor import SetPointSensor

IDX = 10
SVALUE1 = 12.5

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
    sens_col = sensor_collection.reg2sensor(register_definition.TEMP_SETPOINT_CONFORT_A)
    def final():
        sensor_collection.sensorCollection = []
    request.addfinalizer(final)
    return sens_col


@pytest.fixture(scope="function")
def mock_modbus_read(mocker, get_sensor):
    m = mocker.patch.object(get_sensor, 'modbus')
    return mocker.patch.object(m, 'read_register')


def test_sensor_setpoint_check_class_type(get_sensor):
    assert True == isinstance(get_sensor, SetPointSensor)


def test_sensor_setpoint_json_parameter_exception(get_sensor):
    with pytest.raises(ValueError):
        get_sensor.build_json_param()


def test_sensor_setpoint_json_parameter_building(get_sensor):
    sensor = get_sensor
    data = 10
    sensor.set_cache_value(data)
    lcl_json_str = '{"idx": ' + str(sensor.id) + ', "svalue": "' + str(sensor.get_cache_value()) + '"}'
    json_str = sensor.build_json_param()
    assert json_str == lcl_json_str


def test_sensor_setpoint_check_num_of_dec(get_sensor):
    sensor = get_sensor
    assert sensor.num_of_decimal == 1


def test_sensor_setpoint_json_parameter_extraction(get_sensor):
    print(sensor_collection.id2sensor(10).__class__.__name__)
    sens, value = extract_fields_from_json_msg(json_temperature_str)
    assert sens.id == IDX
    assert value == SVALUE1


@pytest.mark.parametrize("temperature, returned_value", [(9, -1), (10, 0), (79, 0), (80, 0), (81, -1)])
def test_sensor_setpoint_set_value_storage(get_sensor, mocker, temperature, returned_value):
    sensor = get_sensor
    mocker.patch.object(sensor, 'set_sensor_value', return_value=returned_value)
    assert returned_value == sensor.set_sensor_value(temperature)


@pytest.mark.parametrize("sens, min, max", [(register_definition.TEMP_SETPOINT_CONFORT_A, 14, 24),
                                            (register_definition.TEMP_SETPOINT_ECO_B, 12, 20),
                                            (register_definition.TEMP_SETPOINT_FREEFROST_B, 0.5, 16),
                                            (register_definition.TEMP_SETPOINT_ECS, 50, 80)])
def test_sensor_setpoint_check_min_max_temp(sens, min, max):
    sensor_collection.build_sensor_collection()
    sensor = sensor_collection.reg2sensor(sens)
    assert sensor.temp_min == min
    assert sensor.temp_max == max


@pytest.mark.parametrize("temp, round_temp", [(17.2, 17.0), (17.4, 17.5), (17.6, 17.5), (17.8, 18.0)])
def test_sensor_setpoint_round_temp(get_sensor, mocker, temp, round_temp):
    sensor = get_sensor
    m = mocker.patch.object(mocker.patch.object(sensor, 'modbus'), 'write_register')
    sensor.set_sensor_value(temp)
    m.assert_called_with(register_definition.TEMP_SETPOINT_CONFORT_A, round_temp, 1)
