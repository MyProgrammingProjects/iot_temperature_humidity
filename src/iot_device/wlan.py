import network
from time import sleep
import ujson
import exceptions.wifi_exceptions as wifi_exceptions
import logger

# Wi-Fi Status Codes in MicroPython
STAT_IDLE = 0              # No connection, Wi-Fi is inactive
STAT_CONNECTING = 1        # Connecting to a Wi-Fi network
STAT_WRONG_PASSWORD = 2    # Incorrect Wi-Fi password
STAT_NO_AP_FOUND = 3       # Access Point (AP) not found
STAT_GOT_IP = 4 

class WlanSettings:
    def __init__(self, 
                 sSsid,
                 sPassword,
                 iRetriesCount):
        self.ssid=sSsid
        self.password=sPassword
        self.retries_count=iRetriesCount

    def AsJson(self):
        logger.log_info(ujson.dumps(self.__dict__))


class WLANClient:
    def __init__(
        self,
        wlanSettings:WlanSettings
    ):
        self.wlanSettings = wlanSettings

    def Reconnect(self, wait_time_between_retries: int):
        self.wlan = network.WLAN(network.STA_IF)
        if not self.wlan.isconnected():
            logger.log_info('Connecting to WiFi')
            self.wlan.active(True)
            self.wlan.connect(self.wlanSettings.ssid, self.wlanSettings.password)

            self.wlanSettings.AsJson()
            connected = False

            for i in range(self.wlanSettings.retries_count):
                # Check Wi-Fi status
                status = self.wlan.status()
                if status < STAT_IDLE or status >= STAT_NO_AP_FOUND:
                    connected = True
                    print('IP Address:', self.wlan.ifconfig()[0])
                    break
                logger.log_info('.')
                sleep(wait_time_between_retries)

            return connected

    # Function: Connect to WiFi
    def Connect(self):
        connected = self.Reconnect(5)

        if(not connected):
            for i in range(self.wlanSettings.retries_count):
                self.Reconnect(30)
        
        if self.wlan.isconnected():
            logger.log_info(f"WiFi Connection established / WiFi Status: {self.wlan.status()}")
            sleep(0.5)

        else:
            logger.log_warn('No WiFi Connection')
            logger.log_warn(f"WiFi Status: {self.wlan.status()}")
            raise wifi_exceptions.WifiConnectionException('No WiFi Connection')