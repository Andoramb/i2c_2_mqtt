# :satellite: Welcome I2C Relay to MQTT! :electric_plug:

This repo can be used to control a Dockerpi relay hat for the Raspberry Pi over MQTT, but it might work for other I2C-type relays.

To get started, even before this repo, check this nice [tutorial page](https://notenoughtech.com/rpi-hat/dockerpi-4-channel-relay/).

## Basic implementation:
### Main functions
 1. Fill in the `config.yaml` with your settings
 2. The script listens on a predefined MQTT topic (`command_topic`) and
    forwards the requests to the relays on I2C protocol.
 3. At the same time, if a relay state is changed, it updates the
    `state_topic`

### Secondary functions

 - Configure it as a service for autostart :gear:
 - Enable HomeAssistant discovery :house_with_garden:

## Functionalities of the script :toolbox:

 1. Change the state of the relays based on MQTT messages
 2. Configurable settings for MQTT and I2C  addresses
 3. HomeAssistant discovery
 4. Online state monitoring on MQTT -> could be enhanced
 5. Configurable service template for autostart on boot -> could be enhanced
 6. Last will messages on MQTT -> tbd

## Get started :rocket:

Are you interested? Cool, let's go:
 1. Clone the repo -> `git clone https://github.com/Andoramb/i2c_2_mqtt.git`
 2. Install prerequisites with `pip install -r requirements.txt`
 3. Fill in `config.yaml`, according to your needs (explanation in the file itself)
 4. Run `python3 mqtt2i2c.py config.yaml`and check the output.
    1. Upon succsessful connect, it should output `Connected with result code 0` :thumbsup:
    2. The state topic should be `online` :white_check_mark:
 5. Check MQTT so the states are reported:
    1. Possible values for toggling to ON state: "on", "1", "true", "ON", "TRUE", "True"
    2. Possible values for toggling to OFF state: "off", "0", "false", "OFF", "FALSE", "False"
    3. However, the app will report `"on"` or `"off"` string only :bulb:
 6. Optional: HomeAsisstant should register the relay based on `device_name` from config.yaml :house_with_garden:
 7. Optional: copy the service template to `/etc/systemd/system` for autostart
    1. Replace `username` and `/path/to/i2c_2_mqtt/` with your data :gear:
    2. `sudo systemctl daemon-reload`
    3. `sudo systemctl enable i2c_2_mqtt.service`
    4. :thumbsup:


## Future improvements :thought_balloon:

Not sure yet, seems to be working :man_shrugging:
