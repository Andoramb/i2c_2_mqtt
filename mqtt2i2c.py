import yaml
import json
import smbus
import paho.mqtt.client as mqtt
import sys

if len(sys.argv) < 2:
    print("Usage: python mqtt2i2c.py <config_file.yaml>")
    sys.exit(1)

# Load the configuration from the YAML file
with open(sys.argv[1], "r") as f:
    config = yaml.safe_load(f)

# MQTT broker configuration
MQTT_BROKER = config["mqtt"]["broker"]
MQTT_PORT = config["mqtt"]["port"]
MQTT_USERNAME = config["mqtt"]["username"]
MQTT_PASSWORD = config["mqtt"]["password"]
MQTT_STATE_TOPIC = config["mqtt"]["state_topic"]
MQTT_COMMAND_TOPIC = config["mqtt"]["command_topic"]

#HomeAsisstant configuration
HA_DISCOVERY_ENABLE = config["homeassistant"]["discovery"]
HA_DISCOVERY = config["homeassistant"]["discovery_prefix"]

# I2C configuration
I2C_DEVICE_ADDRESS = config["i2c"]["device_address"]
I2C_REGISTER_ADDRESS = config["i2c"]["register_address"]

DEVICE_NAME = config["device_name"]

# Connect to I2C bus
bus = smbus.SMBus(1)

STATE_TOPIC = 'I2C/'+DEVICE_NAME+'/'+MQTT_STATE_TOPIC
COMMAND_TOPIC = 'I2C/'+DEVICE_NAME+'/'+MQTT_COMMAND_TOPIC

def on_connect(client, userdata, flags, rc):
    if rc == 0:
      client.subscribe(STATE_TOPIC)
      client.subscribe(COMMAND_TOPIC+"/#")
      report_state()
    else:
        print("Connection failed with result code: ", rc)

    #HomeAssistant: send atodiscovery telemetry for this power switch
    if HA_DISCOVERY_ENABLE == "true":
        data = {
          "name": DEVICE_NAME,
          "state_topic": STATE_TOPIC+"/1",
          "command_topic": COMMAND_TOPIC+"/1",
          "payload_off ": "off",
          "payload_on": "on",
          "icon": "mdi:power",
          "availability": [
            {
                "topic": STATE_TOPIC+"/availability"
            }
           ],
        }
        payload = json.dumps(data)

        client.publish(STATE_TOPIC+'/availability', "online")

        client.publish(HA_DISCOVERY+'/switch/'+DEVICE_NAME+'/config', payload)
        print("Sent HA switch discovery "+str(payload))

# MQTT callback for when a message is received on the subscribed topic
def on_message(client, userdata, msg):
    if userdata["is_updating_state"]:
        return
    relay_number = int(msg.topic.split("/")[-1])

    onlist  = ["on",  "1", "true",  "On",  "ON",  "TRUE",  "True"]
    offlist = ["off", "0", "false", "Off", "OFF", "FALSE", "False"]

    if msg.payload.decode() in onlist:
        # toggle the relay to on
        bus.write_byte_data(I2C_DEVICE_ADDRESS, I2C_REGISTER_ADDRESS[relay_number], 0x01)
    elif msg.payload.decode() in offlist:
        # toggle the relay to off
        bus.write_byte_data(I2C_DEVICE_ADDRESS, I2C_REGISTER_ADDRESS[relay_number], 0x00)
    report_state(relay_number)

def report_state(relays=None):
    if relays is not None and relays > 0:
        current_state = bus.read_byte_data(I2C_DEVICE_ADDRESS, relays)
        current_state = "Off" if current_state == 0 else "On"
        client.publish("{}/{}".format(STATE_TOPIC, str(relays)), current_state)
    else:
        for address in I2C_REGISTER_ADDRESS:
            current_state = bus.read_byte_data(I2C_DEVICE_ADDRESS, address)
            current_state = "Off" if current_state == 0 else "On"
            client.publish("{}/{}".format(STATE_TOPIC, str(address)), current_state)

# Connect to MQTT broker
client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect

# Subscribe to the specified topic
client.user_data_set({"is_updating_state": False})

client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
# Start the MQTT client loop
client.loop_forever()
