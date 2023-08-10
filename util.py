import json
import logging
import sensor.sensor_collection as sensor_collection

from register_definition import TYPE_THERMOSTAT, TYPE_ECS, TYPE_PROG, TYPE_HEATER, \
    TYPE_ALERT, TYPE_DEROG, TYPE_ECS_WEEK

SVALUE1="svalue1"
NVALUE="nvalue"

type2field ={
    TYPE_THERMOSTAT: "svalue1",
    TYPE_HEATER: "svalue1",
    TYPE_PROG: "svalue1",
    TYPE_ALERT: "svalue1",
    TYPE_DEROG: "svalue1",
    TYPE_ECS: "nvalue",
    TYPE_ECS_WEEK: "nvalue"
}

def string2float(jsonString):
    # Check if it's really a number
    if jsonString.replace('.', '', 1).isdigit():
        # if yes save it as float
        return float(jsonString)
    else:
        logging.debug("Field is not numeric value (%s)" % jsonString)
        jsonString


def is_sensor_uptable(sensor):
    uptable = False
    if sensor is not None:
        uptable = sensor.write_enable

    return uptable


def extract_fields_from_json_msg(msg):
    """
    Extract Sensor index & Sensor value from JSON message
    :param msg: JSON message containing value to extract
    :return: sensor index/sensor value couple of None/None if error
    """
    if "<class 'bytes'>" == str(type(msg)):
        msg = msg.decode("utf8")

    data = json.loads(msg)
    idx = data.get("idx")
    value = None

    if idx is not None:
        sensor = sensor_collection.id2sensor(idx)
        if sensor is not None:
            sensor_type = sensor.sensor_type
            field_name = type2field.get(sensor_type, None)
            if sensor.write_enable:
                value = sensor.format_extracted_json_field(data.get(field_name))
                if value is None:
                    logging.error("Unable to recover value for %s" % sensor)
                    sensor = None
            else:
                logging.debug("Write not enable for sensor(%d) %s " %(sensor.id, sensor))
                sensor = None
        else:
            logging.debug("Unknown sensor ID %d" % idx)

    else:
        logging.debug("Unknown index from msg\n\t==>%s" %msg)

    return sensor, value
