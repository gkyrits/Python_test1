import board as brd
import time as tm
import threading as thrd

LED_LUM	= 100

sense=None

def hello():
    if sense == None:
        return         
    sense.show_message("Hello", text_colour=[0,       LED_LUM, 0])
    sense.show_message("Sense", text_colour=[0,       0,       LED_LUM])
    sense.show_message("Hat"  , text_colour=[LED_LUM, 0,       0])

def init():
    global sense
    try:
        from sense_hat import SenseHat
        sense = SenseHat()
        sense.clear()
        sense.set_rotation(90)
        init_buttons()
        thrd.Timer(1,hello).start()
        brd.beep(500)
        brd.beep(1000)
        brd.beep(1500)
    except Exception as e:
        print("Error importing SenseHat: ", e.__str__())
        return    

def sense_exist():
    if sense != None:
        return True
    else:
        return False

def loy_any_pressed(event):
    from sense_hat import ACTION_RELEASED
    if event.action != ACTION_RELEASED:
        brd.beep(2000)
        hello()


def init_buttons():
    if sense == None:
        return     
    sense.stick.direction_up = None
    sense.stick.direction_down = None
    sense.stick.direction_left = None
    sense.stick.direction_right = None
    sense.stick.direction_middle = None
    sense.stick.direction_any = loy_any_pressed

if __name__ == '__main__':
    print("Start Tests")
    init()
    print("press a key for end")
    x=input()
    print("End...")  

