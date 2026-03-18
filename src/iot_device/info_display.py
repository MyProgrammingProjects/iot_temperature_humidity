from machine import Pin, SoftI2C
from time import sleep
from drivers.pico_i2c_lcd import I2cLcd
from drivers.pico_console import LcdConsole
import settings.lcd_config as lcd_config


class InfoDisplay:
    def __init__(self):
        if(lcd_config.I2C_LCD_PRESENT):
            print("Initializing LCD display")
            # Initialize I2C and LCD objects
            self.i2c_lcd = SoftI2C(sda=Pin(lcd_config.I2C_LCD_SDA_PIN), scl=Pin(lcd_config.I2C_LCD_SCL_PIN), freq=lcd_config.I2C_LCD_FREQ)
            self.lcd = I2cLcd(self.i2c_lcd, lcd_config.I2C_LCD_ADDR, lcd_config.I2C_LCD_NUM_ROWS, lcd_config.I2C_LCD_NUM_COLS)
        else:
            self.i2c_lcd = None
            self.lcd = LcdConsole()

    def clear(self):
        self.lcd.clear()

    def putstr_line1(self, msg):
        self.lcd.putstr_line1(msg)

    def putstr_line2(self, msg):
        self.lcd.putstr_line2(msg)

    def display_info(self, msg_line1, msg_line2):
        self.lcd.clear()
        self.lcd.putstr_line1(msg_line1)
        self.lcd.putstr_line2(msg_line2)
        sleep(1)

    def display_info_debug(self, msg_line1, msg_line2):
        if(lcd_config.I2C_LCD_PRESENT == False):
            print(f"Debug: {msg_line1} - {msg_line2}")