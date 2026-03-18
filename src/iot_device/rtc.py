import machine 
import utime
import usocket as socket
import ustruct as struct
from time import gmtime
import ujson
import logger

class RtcSettings:
    def __init__(self, 
                 sNtpServer):
        self.ntp_server=sNtpServer

    def AsJson(self):
        logger.log_info(ujson.dumps(self.__dict__))


class TimeTuple:
    def __init__(self, 
                 year, month, day, hours, minutes, seconds, weekday, yearday):
        self.year=year
        self.month=month
        self.day=day
        self.hours=hours
        self.minutes=minutes
        self.seconds=seconds
        self.weekday=weekday
        self.yearday=yearday

class RTCClient:
    def __init__(self, rtcSettings:RtcSettings):
        self.RtcSettings =rtcSettings

    # Function: Get Time via NTP
    def Connect(self):
        self.RtcSettings.AsJson()

        NTP_DELTA = 2208988800
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        addr = socket.getaddrinfo(self.RtcSettings.ntp_server, 123)[0][-1]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.settimeout(10)
            logger.log_info('start call sendto for ntp query')
            res = s.sendto(NTP_QUERY, addr)
            logger.log_info('end call sendto for ntp query')
            msg = s.recv(48)
        finally:
            s.close()
        ntp_time = struct.unpack("!I", msg[40:44])[0]
        # Unpacks the 4 bytes as an unsigned integer in network byte order ("!I").

        #(year, month, day, hours, minutes, seconds, weekday, yearday)
        (year, month, day, hours, minutes, seconds, weekday, _) = gmtime(ntp_time - NTP_DELTA)
        return TimeTuple(year, month, day, hours, minutes, seconds, weekday, _)


    # Function: Set RTC time
    def setTimeRTC(self,tm:TimeTuple):
        machine.RTC().datetime((tm.year, tm.month, tm.day, tm.weekday, tm.hours, tm.minutes, tm.seconds, 0))
        
        current_time = utime.localtime()
        formatted_date = "{:04d}/{:02d}/{:02d} {:02d}:{:02d}".format(
                current_time[0],  # Year
                current_time[1],  # Month
                current_time[2],  # Day
                current_time[3],  # Hour
                current_time[4]   # Minute
            )
        logger.log_info(formatted_date)
