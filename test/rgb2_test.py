from gpiozero import RGBLED,Buzzer
from time import sleep

led = RGBLED(red=29, green=28, blue=30)
bz  = Buzzer(31)

VAL = 10

colors = {"white":(VAL,VAL,VAL), "red":(VAL,0,0), "green":(0,VAL,0), "blue":(0,0,VAL),
          "yellow":(VAL,VAL,0), "aqua":(0,VAL,VAL), "fuchsia":(VAL,0,VAL),
          "black":(0,0,0)
          }

def play_colors():
    col_list = list(colors.keys())
    for col in col_list[:7]:
        print("%s" % col)
        led.color = (colors[col][0]/255,colors[col][1]/255,colors[col][2]/255)        
        sleep(1)


while True:
    play_colors()
    bz.beep(0.01,0,1)


