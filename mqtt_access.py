#!/usr/bin/python3

import time
import queue
import paho.mqtt.client as mqtt

from prj_logger import logging
from optparse import OptionParser
from os import environ as DOMOTICZ_ENV

usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)
parser.set_defaults(stub=False)
parser.add_option("-s", "--stubbed", dest="stub", action="store_true", help="Activate stubbed read/write")

(options, args) = parser.parse_args()

# don't move the 6 following lines
if options.stub:
    DOMOTICZ_ENV["STUBBED_MODE"] = '1'
    from modbus_stubbed import ModbusStubbed
else:
    DOMOTICZ_ENV["STUBBED_MODE"] = '0'
    from modbus_access import ModbusAccess

from util import extract_fields_from_json_msg, is_sensor_uptable
from sensor.sensor_collection import build_sensor_collection

host = "localhost"  # the address of the mqtt broker
sub_topic = "domoticz/out/#"
pub_topic = "domoticz/in"
port = 1883
write_queue = queue.Queue()
last_idx_updated = None
prev_value_updated = None
mqttc = mqtt.Client()


def on_connect(mqttc, obj, flags, rc):
    print('on_connect() rc=' + str(rc))


def on_message(mqttc, obj, msg):
    write_queue.put(msg.payload)


def on_subscribe(mqttc, obj, mid, granted_qos):
    print('\nSubscribing to ' + sub_topic + "...")
    print("Subscribed OK\n")


def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))


def publish_data(data_str):
    return mqttc.publish(pub_topic, data_str, qos=0)


def on_log(mqttc, obj, level, string):
    print(string)


def mqttc_init():
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_subscribe = on_subscribe

    # mqttc.on_publish = on_publish
    # Uncomment to enable debug messages
    # mqttc.on_log = on_log

    print("Connecting to " + host)
    mqttc.connect(host, port, 60)

    mqttc.loop_start()
    time.sleep(1)


def get_last_published_ctx():
    global last_idx_updated
    global prev_value_updated
    return last_idx_updated, prev_value_updated


def sensor_to_publish(json, idx, cur_value):
    global last_idx_updated
    global prev_value_updated

    publish_data(json)
    last_idx_updated = idx
    prev_value_updated = cur_value

def is_sensor_need_update(sens, cur_value):
    is_updatable = False
    prev_id, prev_value = get_last_published_ctx()

    if is_sensor_uptable(sens):
        if (cur_value is None) and (prev_id == sens.id) and (prev_value == cur_value):
            logging.debug("Update not required for(idx = %d, value = %d)" % (sens.id, cur_value))
        else:
            is_updatable = True
    else:
        logging.debug("Sensor not updatable %s" % sens)

    return is_updatable


def broker_initialisation():
    print("Inialization STARTING... All messages will be rejected during initialization")

    for sens in sensor_collection:
        sens.is_time2monitor()

    mqttc.subscribe(sub_topic, 0)
    for sens in sensor_collection:
        try:
            json_element = write_queue.get(timeout=0.5)
            logging.debug("Initialization in progress reject element %s" % json_element)
        except queue.Empty:
            logging.debug("Initialization in progress, element not received")

    logging.info("************************Initialization done...************************")


mqttc_init()
sensor_collection = build_sensor_collection(json_sending_method=sensor_to_publish, modbus_obj=ModbusAccess())
initialization_done = False
broker_initialisation()
while True:
    prev_idx = prev_value = 0
    try:
        while True:
            writeelement = write_queue.get(timeout=1)
            sensor, value = extract_fields_from_json_msg(writeelement)

            if is_sensor_need_update(sensor, value):
                if sensor.get_cache_value() != value:
                    sensor.set_sensor_value(value)
    except queue.Empty:
        pass

    for sensor in sensor_collection:
        sensor.is_time2monitor()