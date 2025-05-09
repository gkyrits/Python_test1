# /*****************************************************************************
# * | File        :	  epdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2019-06-21
# * | Info        :   
# ******************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import sys
import time
import spidev
#import logging
import numpy as np
from gpiozero import *

USE_PIGPIO=True

class RaspberryPi:
    def __init__(self, spi_dev=0, spi_cs=0, spi_freq=32000000, rst=25, dc=24, bl=22, bl_freq=1000):
        self.np=np
        self.INPUT = False
        self.OUTPUT = True

        self.SPEED  =spi_freq
        self.BL_freq=bl_freq
        self.BL_duty=10
        self.pi=None #for pigpio lib

        self.RST_PIN= self.gpio_mode(rst,self.OUTPUT)
        self.DC_PIN = self.gpio_mode(dc,self.OUTPUT)
        self.BL_PIN = self.gpio_pwm(bl)
        self.bl_DutyCycle(self.BL_duty)
        
        #Initialize SPI    
        self.SPI = spidev.SpiDev(spi_dev,spi_cs)
        if self.SPI!=None :
            self.SPI.max_speed_hz = spi_freq
            self.SPI.mode = 0b00

    def gpio_mode(self,Pin,Mode,pull_up = None,active_state = True):
        if Mode:
            return DigitalOutputDevice(Pin,active_high = True,initial_value =False)
        else:
            return DigitalInputDevice(Pin,pull_up=pull_up,active_state=active_state)

    def digital_write(self, Pin, value):
        if value:
            Pin.on()
        else:
            Pin.off()

    def digital_read(self, Pin):
        return Pin.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def gpio_pwm(self,Pin):
        if USE_PIGPIO:
            import pigpio
            self.pi=pigpio.pi()
            dcycle=self.BL_duty*10000
            self.pi.hardware_PWM(Pin, self.BL_freq, dcycle)
            return Pin
        else:    
            return PWMOutputDevice(Pin,frequency = self.BL_freq)

    def spi_writebyte(self, data):
        if self.SPI!=None :
            self.SPI.writebytes(data)

    def bl_DutyCycle(self, duty):
        self.BL_duty=duty
        if USE_PIGPIO:
            dcycle=duty*10000
            self.pi.hardware_PWM(self.BL_PIN, self.BL_freq, dcycle)
        else:    
            self.BL_PIN.value = duty / 100
        
    def bl_Frequency(self,freq):# Hz
        self.BL_freq=freq
        if USE_PIGPIO:
            dcycle=self.BL_duty*10000
            self.pi.hardware_PWM(self.BL_PIN, freq, dcycle)            
        else:    
            self.BL_PIN.frequency = freq
           
    def module_init(self):
        if self.SPI!=None :
            self.SPI.max_speed_hz = self.SPEED        
            self.SPI.mode = 0b00     
        return 0

    def module_exit(self):
        #logging.debug("spi end")
        print("lcd module_exit")
        if self.SPI!=None :
            self.SPI.close()
        
        #logging.debug("gpio cleanup...")
        self.digital_write(self.RST_PIN, 1)
        self.digital_write(self.DC_PIN, 0)   
        if USE_PIGPIO:
            self.pi.hardware_PWM(self.BL_PIN, self.BL_freq, 0)
            self.pi.stop()
        else:    
            self.BL_PIN.close()
        time.sleep(0.001)



'''
if os.path.exists('/sys/bus/platform/drivers/gpiomem-bcm2835'):
    implementation = RaspberryPi()

for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))
'''

### END OF FILE ###
