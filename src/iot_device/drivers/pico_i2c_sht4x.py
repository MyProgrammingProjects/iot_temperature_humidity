from time import sleep

# SHT4x default I2C address
SHT4x_ADDR = 0x44

# Commands
MEASURE_HIGH_PRECISION = b'\xFD'  # Command for high precision measurement

class SHT4x:
    def __init__(self, i2c, addr=SHT4x_ADDR):
        self.i2c = i2c
        self.addr = addr

    def read_temperature_humidity(self):
        # Send measurement command
        self.i2c.writeto(self.addr, MEASURE_HIGH_PRECISION)
        
        # Wait for the measurement to complete (typical max time is 10ms)
        sleep(0.02)
        
        # Read 6 bytes of data
        data = self.i2c.readfrom(self.addr, 6)
        
        # Convert the bytes to temperature and humidity
        temp_raw = data[0] << 8 | data[1]
        humidity_raw = data[3] << 8 | data[4]
        
        # Calculate temperature in Celsius
        temperature = -45 + 175 * (temp_raw / 65535.0)
        
        # Calculate relative humidity
        humidity = 100 * (humidity_raw / 65535.0)
        
        return temperature, humidity
