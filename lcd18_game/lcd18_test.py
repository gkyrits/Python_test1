#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys
import time
import logging
import spidev as SPI
#sys.path.append("..")
#from lib import LCD_1inch8
import lcd18driver as lcd
from PIL import Image,ImageDraw,ImageFont

# Raspberry Pi pin configuration:
RST = 25
DC = 24
BL = 22
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)
try:
    # display with hardware SPI:
    ''' Warning!!!Don't  creation of multiple displayer objects!!! '''
    #disp = lcd.LCD_1inch8(spi=SPI.SpiDev(bus, device),spi_freq=10000000,rst=RST,dc=DC,bl=BL)
    disp = lcd.LCD_1inch8()
    # Initialize library.
    disp.Init()
    # Clear display.
    disp.clear()
    #Set the backlight to 100
    disp.bl_DutyCycle(50)

    # Create blank image for drawing.
    image = Image.new("RGB", (disp.width, disp.height), "WHITE")
    draw = ImageDraw.Draw(image)
    font18 = ImageFont.truetype("Font/Font00.ttf",18) 

    logging.info("draw point")

    draw.rectangle((1, 1,2, 2), fill = "BLACK")
    draw.rectangle((1, 7,3,9), fill = "BLACK")
    draw.rectangle((1,14,4,17), fill = "BLACK")
    draw.rectangle((1,21,5,25), fill = "BLACK")
    disp.ShowImage(image)
    time.sleep(1)

    logging.info("draw line")
    draw.line([(10, 5),(40,35)], fill = "RED",width = 1)
    draw.line([(10,35),(40, 5)], fill = "RED",width = 1)
    draw.line([(80,20),(110,20)], fill = "RED",width = 1)
    draw.line([(95, 5),(95,35)], fill = "RED",width = 1)
    disp.ShowImage(image)
    time.sleep(1)    

    logging.info("draw rectangle")
    draw.rectangle([(10,5),(40,35)],fill = "WHITE",outline="BLUE")
    draw.rectangle([(45,5),(75,35)],fill = "BLUE")
    disp.ShowImage(image)
    time.sleep(1)    

    logging.info("draw circle")
    draw.arc((80,5,110,35),0, 360, fill =(0,255,0))
    draw.ellipse((115,5,145,35), fill = (0,255,0))
    disp.ShowImage(image)
    time.sleep(1)    

    logging.info("draw text")
    Font1 = ImageFont.truetype("Font/Font01.ttf",16)
    Font2 = ImageFont.truetype("Font/Font01.ttf",20)
    Font3 = ImageFont.truetype("Font/Font02.ttf",25)    
    draw.text((5, 40), 'Hello world', fill = "BLACK",font=Font1)
    disp.ShowImage(image)
    time.sleep(1)     
    draw.text((5, 60), 'WaveShare', fill = "RED",font=Font2)
    disp.ShowImage(image)
    time.sleep(1)     
    draw.text((5, 80), '1234567890', fill = "GREEN",font=Font1)
    disp.ShowImage(image)
    time.sleep(1)     
    text= u"ΑΛΦΑβήτα"    
    draw.text((5, 100),text, fill = "BLUE",font=Font3)    
    #im_r=image.rotate(90)
    disp.ShowImage(image)

    for x in [40,30,20,10,20,30,40,50,60,70,80,90,100,90,80,60,50]:
        disp.bl_DutyCycle(x)
        time.sleep(0.2)

    logging.info("show image")
    #image = Image.open('pic/LCD_1inch8.jpg')	
    image = Image.open('pic/cat.jpg')
    image = image.resize((disp.width, disp.height))
    #im_r=image.rotate(0)
    disp.ShowImage(image)
    
    while True:
        time.sleep(1)
    
    disp.module_exit()
    logging.info("quit1:")
    
except IOError as e:
    logging.info(e)    
except KeyboardInterrupt:
    disp.module_exit()
    logging.info("quit2:")
    exit()
