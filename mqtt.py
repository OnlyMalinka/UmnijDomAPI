import json
import random
import time
import paho.mqtt.client as paho
from paho import mqtt
import db
import secret
client = paho.Client(client_id=f"API-{random.randint(0,9999)}", userdata=None, protocol=paho.MQTTv5,
                     callback_api_version=paho.CallbackAPIVersion.VERSION1)
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNECT received with code %s." % rc)
def on_message(client, userdata, msg):
    match msg.topic.split('/')[-1]:
        case "first_connection":
            payload_dict = json.loads(msg.payload.decode("utf-8"))
            mac = payload_dict["mac"]
            device_type = payload_dict["type"]
            result=db.add_waiting_device(mac, device_type)
            if (result!=True):print(f"Error mqtt first_connection: {result}")
        case "status":
            status = msg.payload.decode("utf-8")
            result=db.change_device_status_by_mac(msg.topic.split('/')[-2].replace("device_", ""), status)
            if (result != True): print(f"Error mqtt status: {result}")
        case "pong":
            result=db.change_device_connection(msg.topic.split('/')[-2].replace("device_", ""), "online")
            if (result != True): print(f"Error mqtt pong: {result}")
        case "turning on":
            try:
                device = db.get_device_by_mac(msg.topic.split('/')[-2].replace("device_", ""))[0]
                all_data = db.get_device_data(device['device_id'])
                publish(f"devices/device_{device['mac']}/status", device['status'])
                for data in all_data:
                    if data['data_drawer'] != "Sensor":
                        publish(f"devices/device_{device['mac']}/{data['name_in_code']}", data['value'])
            except Exception as e:
                print(f"Error mqtt turning on: {e}")
        case "sensor":
            try:
                payload_dict = json.loads(msg.payload.decode("utf-8"))
                device_mac = msg.topic.split('/')[-2].replace("device_", "")
                data_name = payload_dict["name"]
                data_value = payload_dict["value"]
                device_id = db.get_device_by_mac(device_mac)[0]['device_id']
                data_id = db.get_data_type_by_name(data_name)['type_id']
                result=db.add_or_change_device_data(device_id, data_id, data_value)
                if (result != True): print(f"Error mqtt sensor: {result}")
            except Exception as e:
                print(f"Error mqtt sensor: {e}")
        case "start_value":
            try:
                payload_dict = json.loads(msg.payload.decode("utf-8"))
                data_name = payload_dict["name"]
                data_value = payload_dict["value"]
                device_id = db.get_device_by_mac(msg.topic.split('/')[-2].replace("device_", ""))[0]['device_id']
                data_id = db.get_data_type_by_name(data_name)['type_id']
                result = db.add_or_change_device_data(device_id, data_id, data_value)
                if (result != True): print(f"Error mqtt sensor: {result}")
            except Exception as e:
                print(f"Error mqtt sensor: {e}")
        case _:
            if (msg.topic.split('/')[-1]!="ping" and msg.topic.split('/')[-1]!="pong"):
                print("Message received: " + msg.payload.decode("utf-8")+ " || on topic " + msg.topic + " || with QoS " + str(msg.qos))

def publish(topic, payload):
    client.publish(topic, payload=payload, qos=1)
def start_mqtt():
    client.on_connect = on_connect
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(secret.username, secret.password)
    client.connect(secret.mqttadress, 8883)
    client.on_message = on_message
    client.subscribe("#", qos=1)
    client.loop_start()
