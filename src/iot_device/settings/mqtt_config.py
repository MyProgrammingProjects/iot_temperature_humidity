MQTT_CLIENT_ID = "<device>"
MQTT_SERVER = "<server>.azure-devices.net"
MQTT_USERNAME = f"{MQTT_SERVER}/{MQTT_CLIENT_ID}/?api-version=2021-04-12"
MQTT_PASSWORD = ""  #empty since authentication will be made using CA signed certificate
MQTT_PORT=8883
MQTT_KEEP_ALIVE=7200
#$.ct=application%2Fjson%3Bcharset%3Dutf-8 is mandatory to prevent request body from being save as base64
MQTT_TOPIC=f"devices/{MQTT_CLIENT_ID}/messages/events/$.ct=application%2Fjson%3Bcharset%3Dutf-8"

