import sys
import json
import time
import paho.mqtt.client as mqtt
from truck import Truck

client_name, client_token = sys.argv[1], sys.argv[2]

def log(message):
    print("{0}: {1}".format(client_name, message))


log("Starting truck".format(client_name))
truck = Truck(client_name)
 
def on_connect(client, userdata, flags, rc):
    print("Received result code "+str(rc))
    if rc != 0:
        log('Connection failed. Trying to reconnect in a moment.')
    else:
        client.subscribe("v1/devices/me/rpc/request/+")

def on_message(client, userdata, msg):
    log(msg.topic+" "+str(msg))
    payload = json.loads(msg.payload)
    if payload['method'] == 'getValue':
        msg_id = msg.topic.rsplit('/', 1)[-1]
        client.publish("v1/devices/me/rpc/response/" + msg_id, truck.speed)
    elif payload['method'] == 'setValue':
        truck.speed = int(payload['params'])

def on_publish(client, userdata, mid):
    log("Message delivered.")

log("Registering.")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Wait for 20 seconds for related services to start. After that connect
log("Sleeping for 10 seconds before connecting".format(client_name))
time.sleep(10)
client.username_pw_set(client_token)
client.connect("tb", 1883, 60)

client.loop_start()
while True:
    client.publish("v1/devices/me/telemetry", json.dumps(truck.update()))
    time.sleep(2)