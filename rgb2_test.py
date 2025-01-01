from gpiozero import LED,RGBLED,Buzzer
from time import sleep

led = RGBLED(red=29, green=28, blue=30)
bz = Buzzer(31)


TIME=4.0
MAX_RED=20
MAX_GREEN=15
MAX_BLUE=100

red_wait=TIME/MAX_RED
green_wait=TIME/MAX_GREEN
blue_wait=TIME/MAX_BLUE

colors = {"white":(255,255,255), "red":(255,0,0), "green":(0,255,0), "blue":(0,0,255),
          "yellow":(255,255,0), "aqua":(0,255,255), "fuchsia":(255,0,255)
          ,"black":(0,0,0)
          }

def play_colors():
    for col in colors.keys():
        print("%s" % col)
        led.color = (colors[col][0]/255,colors[col][1]/255,colors[col][2]/255)        
        sleep(1)


while True:
    play_colors()
    bz.beep(0.01,0,1)


