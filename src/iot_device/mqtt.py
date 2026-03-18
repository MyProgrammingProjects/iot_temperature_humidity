####################################################
# imports
####################################################
from umqtt.simple import MQTTClient
import ujson
import ssl
import exceptions.mqtt_exceptions as mqtt_exceptions
import logger

class MqttSettings:
    def __init__(self, 
                sMqttServer,
                sMqttUsername,
                sMqttPassword,
                sMqttClientId,
                iMqttPort,
                iMqttKeepAlive,
                sMqttCertPath,
                sMqttCertKeyPath,
                sMqttMessagesPath
                ):
        self.mqttServer=sMqttServer
        self.mqttUsername=sMqttUsername
        self.mqttPassword=sMqttPassword
        self.mqttClientId=sMqttClientId
        self.mqttPort=iMqttPort
        self.iMqttKeepAlive=iMqttKeepAlive
        self.mqttCertPath=sMqttCertPath
        self.mqttCertKeyPath=sMqttCertKeyPath
        self.mqttMessagesPath=sMqttMessagesPath

    def AsJson(self):
        logger.log_trace(ujson.dumps(self.__dict__))


class MyMQTTClient:
    def __init__(self, 
                mqttSettings:MqttSettings):
        self.mqttSettings=mqttSettings

    def get_ssl_certificate(self):
        logger.log_trace('Loading Certificate')
        with open(self.mqttSettings.mqttCertPath, 'rb') as f:
            DEVICE_CERT = f.read()

        logger.log_trace('Loading Certificate Key')
        with open(self.mqttSettings.mqttCertKeyPath, 'rb') as f:
            DEVICE_KEY = f.read()
        return (DEVICE_CERT, DEVICE_KEY)        

    
    def Connect(self):

        try:
            (DEVICE_CERT, DEVICE_KEY) = self.get_ssl_certificate()
            MQTT_SSL_PARAMS={}
            MQTT_SSL_PARAMS["server_hostname"] = self.mqttSettings.mqttServer
            MQTT_SSL_PARAMS["key"] = DEVICE_KEY
            MQTT_SSL_PARAMS["cert"] = DEVICE_CERT

            #https://github.com/micropython/micropython-lib/issues/811
            #https://github.com/orgs/micropython/discussions/13624
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.verify_mode = ssl.CERT_NONE
            context.load_cert_chain(certfile=DEVICE_CERT, keyfile=DEVICE_KEY)

            self.client = MQTTClient(self.mqttSettings.mqttClientId,
                                self.mqttSettings.mqttServer,
                                self.mqttSettings.mqttPort,
                                self.mqttSettings.mqttUsername,
                                self.mqttSettings.mqttPassword,
                                self.mqttSettings.iMqttKeepAlive,
                                ssl=context)
            self.client.connect()
            logger.log_info('Success connecting to MQTT')
            return self.client
        except Exception as e:
            logger.log_error('Error connecting to MQTT:', e)
            raise mqtt_exceptions.MqttConnectionException(e) # Re-raise the exception to see the full traceback


    def Publish(self, value):
        try:
            self.client.publish(self.mqttSettings.mqttMessagesPath, value)
            logger.log_trace(self.mqttSettings.mqttMessagesPath)
            logger.log_trace(value)
            logger.log_info("Publish Done")
        except Exception as e:
            logger.log_error('Error Publish to MQTT:', e)
            raise mqtt_exceptions.MqttPublishException(e) # Re-raise the exception to see the full traceback

