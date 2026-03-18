####################################################
# imports
####################################################
from machine import I2C, Pin, SoftI2C
from time import sleep, gmtime
import utime
import ujson
import os

import settings.network_config as network_config
import settings.lcd_config as lcd_config
import settings.sensor_config as sensor_config
import settings.mqtt_config as mqtt_config
import settings.rtc_config as rtc_config
import settings.measurements_config as measurements_config

import logger
from mqtt import MqttSettings, MyMQTTClient
from wlan import WLANClient, WlanSettings
from rtc import RTCClient, RtcSettings

from drivers.pico_i2c_sht4x import SHT4x
from info_display import InfoDisplay
import exceptions.wifi_exceptions as wifi_exceptions
import exceptions.mqtt_exceptions as mqtt_exceptions


####################################################
# shared variables
####################################################


LOG_FILE_CORE0 = "log_file_core0.txt"
META_FILE_CORE0 = "log_meta_core0.txt"

MAX_SIZE = 64 * 1024  # 64 kB
CHUNK_SIZE = 64        # Size of each log entry

sensor_data_retrieval_interval = 5  # seconds between sensor data retrieval
unhandled_exception_sleep_seconds = 60
mqtt_connection_exception_sleep_seconds = 60
wifi_connection_exception_sleep_seconds = 120

year_time_index=0
month_time_index=1
day_time_index=2
hour_time_index=3
minute_time_index=4
second_time_index=5


####################################################
# functions
####################################################
def init_logs_Core0():
    if not LOG_FILE_CORE0 in os.listdir():
        with open(LOG_FILE_CORE0, "wb") as f:
            f.write(b'\x00' * MAX_SIZE)

    if not META_FILE_CORE0 in os.listdir():
        with open(META_FILE_CORE0, "w") as f:
            f.write("0")  # Start at position 0

def get_log_pos_Core0():
    with open(META_FILE_CORE0, "r") as f:
        return int(f.read().strip())

def set_log_pos_Core0(pos):
    with open(META_FILE_CORE0, "w") as f:
        f.write(str(pos))


def write_log_Core0(input):
    current_time = utime.gmtime()
    formatted_date = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
        current_time[year_time_index],  # Year
        current_time[month_time_index],  # Month
        current_time[day_time_index],  # Day
        current_time[hour_time_index],  # Hour
        current_time[minute_time_index],   # Minute
        current_time[second_time_index]   # Second
    )

    data = f"{formatted_date} - {input}"
    if isinstance(data, str):
        data = data.encode()
    data = data[:CHUNK_SIZE]  # Truncate if too long
    data += b'\x00' * (CHUNK_SIZE - len(data))  # Pad if too short

    pos = get_log_pos_Core0()

    with open(LOG_FILE_CORE0, "r+b") as f:
        f.seek(pos)
        f.write(data)

    pos = (pos + CHUNK_SIZE) % MAX_SIZE
    set_log_pos_Core0(pos)


####################################################
# program
####################################################

# Initialize information display interface, which can be console or LCD depending on settings.lcd_config
lcd = InfoDisplay()

# Initialize I2C interface
i2c_sensor = I2C(1, scl=Pin(sensor_config.I2C_SENSOR_SCL_PIN), sda=Pin(sensor_config.I2C_SENSOR_SDA_PIN), freq=sensor_config.I2C_SENSOR_FREQ)

# Create SHT4x instance
sensor = SHT4x(i2c_sensor, addr=sensor_config.I2C_SENSOR_ADDR)

init_logs_Core0()


while True:
    try:
        lcd.display_info('Connecting','Wifi')
        write_log_Core0('Connecting Wifi')

        wlanSettings = WlanSettings(network_config.WIFI_SSID, network_config.WIFI_PASSWORD, 30)
        wlanClient = WLANClient(wlanSettings)
        wlanClient.Connect()

        lcd.display_info('Connected','Wifi')
        write_log_Core0('Connected Wifi')
        lcd.display_info('Setting NTP','Server')
        write_log_Core0('Setting NTP Server')

        for ntp_server in rtc_config.NTP_SERVERS:
            try:
                rtcSettings = RtcSettings(ntp_server)
                rtcClient = RTCClient(rtcSettings)
                tm = rtcClient.Connect()
                
                if tm:  # Ensure 'tm' is valid before proceeding
                    rtcClient.setTimeRTC(tm)
                    logger.log_info(f"Connected to get time from {ntp_server}, break")
                    write_log_Core0(f"Connected to get time from {ntp_server}, break")
                    break  # Stop the loop as soon as a connection succeeds
                else:
                    logger.log_info(f"Failed to get time from {ntp_server}, trying next server...")
                    write_log_Core0(f"Failed to get time from {ntp_server}, trying next server...")
            except OSError as e:  # Catch specific network errors
                logger.log_info(f"Network error with {ntp_server}: {e}")
                write_log_Core0(f"Network error with {ntp_server}: {e}")
            except Exception as e:  # Catch other unexpected errors
                logger.log_info(f"Unexpected error with {ntp_server}: {e}")
                write_log_Core0(f"Unexpected error with {ntp_server}: {e}")


        lcd.display_info('Setup NTP','Server Done')
        write_log_Core0('Setup NTP Server Done')

        #certificates must be in DER format to work with uPython (PEM format did not work)
        # https://github.com/orgs/micropython/discussions/13534
        # 'In micropython certificate have to be in DER format not PEM'
        # certificates were generated following Microsoft documentations see README_CERTIFICATES.md
        mqttSettings = MqttSettings(
            mqtt_config.MQTT_SERVER,
            mqtt_config.MQTT_USERNAME,
            mqtt_config.MQTT_PASSWORD,
            mqtt_config.MQTT_CLIENT_ID,
            mqtt_config.MQTT_PORT,
            mqtt_config.MQTT_KEEP_ALIVE,
            './certificates/<certificate>.der',
            './certificates/<certificate_key>.der',
            mqtt_config.MQTT_TOPIC
        )

        # Display two different messages on different lines
        lcd.display_info('Connecting','MQTT')
        write_log_Core0('Connecting MQTT')

        myMQTTClient=MyMQTTClient(mqttSettings)
        mqttClient = myMQTTClient.Connect()

        lcd.display_info('Connected','MQTT')
        write_log_Core0('Connected MQTT')
        
        while True:
            temperature = None
            humidity = None
            current_time = utime.gmtime()
            formatted_date = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}".format(
                current_time[year_time_index],  # Year
                current_time[month_time_index],  # Month
                current_time[day_time_index],  # Day
                current_time[hour_time_index],  # Hour
                current_time[minute_time_index]   # Minute
            )

            for i in range(0,61,sensor_data_retrieval_interval): 
                current_time = utime.gmtime()
                formatted_date = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}".format(
                    current_time[year_time_index],  # Year
                    current_time[month_time_index],  # Month
                    current_time[day_time_index],  # Day
                    current_time[hour_time_index],  # Hour
                    current_time[minute_time_index]   # Minute
                )
                logger.log_info(formatted_date)

                # Read sensor data
                temperature, humidity = sensor.read_temperature_humidity()
                sTemperature = "{:.2f} C".format(temperature)
                sHumidity = "{:.2f} %".format(humidity)
                sValue = sTemperature+'  '+sHumidity
                lcd.display_info(formatted_date,sValue)

                sleep(sensor_data_retrieval_interval)

            data={'device':mqttSettings.mqttClientId  
                , 'room':measurements_config.ROOM
                , 'dataType':measurements_config.DATATYPE
                , 'year':current_time[year_time_index]
                , 'month':current_time[month_time_index]
                , 'day':current_time[day_time_index]
                , 'hour':current_time[hour_time_index]
                , 'minutes':current_time[minute_time_index]
                , 'seconds':current_time[5]
                , 'temperature':{
                    'value': temperature,
                    'unit':measurements_config.TEMPERATURE_UNIT
                    }
                , 'humidity':{
                    'value': humidity,
                    'unit':measurements_config.HUMIDITY_UNIT
                    }
                }
            
            json_string = ujson.dumps(data)
            # Convert the JSON string to byte literals (save has using b'<string>')
            msg = json_string.encode('utf-8') # In MicroPython, strings are Unicode by default
            # Publish as MQTT payload
            logger.log_info('Going to Publish')
            write_log_Core0("Going to Publish")

            myMQTTClient.Publish(msg)
            lcd.display_info(formatted_date,'Sent Data')
            write_log_Core0("Data Sent")

    except mqtt_exceptions.MqttConnectionException as e:
        logger.log_error(f'Error: MqttConnectionException')
        write_log_Core0(f"Error: MqttConnectionException: {e}")
        sleep(mqtt_connection_exception_sleep_seconds) # wait before retrying

    except wifi_exceptions.WifiConnectionException as e:
        logger.log_error(f'Error: WifiConnectionException')
        write_log_Core0(f"Error: WifiConnectionException: {e}")
        sleep(wifi_connection_exception_sleep_seconds) # wait before retrying

    except Exception as e:
        logger.log_error(f'Error Generic')
        write_log_Core0(f"Error Generic: {e}")
        sleep(unhandled_exception_sleep_seconds) # wait before retrying