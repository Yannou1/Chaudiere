#!/usr/bin/env python3
import time
import json
from register_definition import COL_IDX, COL_REGISTER, COL_SENSOR_TYPE, COL_MONITORING_PERIOD, get_system_config
from register_definition import TYPE_THERMOSTAT, TYPE_ECS, TYPE_TEMPERATURE, TYPE_PROG, TYPE_HEATER, \
    TYPE_ALERT, TYPE_DEROG, TYPE_REMOTE, TYPE_ECS_WEEK, VIRTUAL_IDX

import sensor

RETURN_ERROR = -1
RETURN_OK = 0

sensorCollection = []


sensorBuilder = {TYPE_TEMPERATURE: sensor.TempSensor,
                 TYPE_THERMOSTAT: sensor.SetPointSensor,
                 TYPE_ECS: sensor.EcsSensor,
                 TYPE_PROG: sensor.ProgSensor,
                 TYPE_HEATER: sensor.HeaterSensor,
                 TYPE_ALERT: sensor.FreefrostSensor,
                 TYPE_DEROG: sensor.DerogSensor,
                 TYPE_REMOTE: sensor.RemoteSensor,
                 TYPE_ECS_WEEK: sensor.EcsWeekSensor}

def build_sensor_collection(system_config=get_system_config(), json_sending_method=None, modbus_obj=None):
    if len(sensorCollection):
        return sensorCollection

    for sys_config in system_config:
        sensor_type = sys_config[COL_SENSOR_TYPE]

        if __is_virtual_sensor_index(sys_config[COL_IDX]):
            continue

        new_sensor = sensorBuilder[sensor_type](sys_config[COL_REGISTER], sys_config[COL_IDX],
                                                 sys_config[COL_SENSOR_TYPE], reg2sensor, id2sensor, sys_config[COL_MONITORING_PERIOD],
                                                _modbus=modbus_obj, update_ihm=json_sending_method)

        sensorCollection.append(new_sensor)

    return sensorCollection


def get_number_of_virtual_sensor(system_config=get_system_config()):
    nbr = 0
    for sys_config in system_config:
        if __is_virtual_sensor_index(sys_config[COL_IDX]):
            nbr += 1

    return nbr


def __is_virtual_sensor_index(id):
    if id >= VIRTUAL_IDX:
        return True

    return False

def reg2sensor(register):
    for _sensor in sensorCollection:
        if _sensor.register == register:
            return _sensor
    return None


def id2sensor(_id):
    for _sensor in sensorCollection:
        if _sensor.id == _id:
            return _sensor
    return None


def get_sensor_collection():
    if not len(sensorCollection):
        build_sensor_collection()

    return globals(sensorCollection)


if __name__ == '__main__':
    build_sensor_collection()
