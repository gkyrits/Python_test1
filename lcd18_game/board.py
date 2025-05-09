import time as tm
import os

BUZZ_GPIO = 12
KEY1_GPIO = 18
KEY2_GPIO = 17
KEY3_GPIO = 5

FILTER_STEADY=50000
FILTER_ACTIVE=1

pi=None
key1=None
key2=None
key3=None

key1_func=None
key2_func=None
key3_func=None

def init():
    global pi
    try:
        import pigpio
        pi=pigpio.pi()
    except Exception as e:
        print("Error importing pigpio: ", e.__str__())
        return         

def close():
    if pi == None:
        return        
    pi.stop()

def beep(freq=600, time=.1):
    if pi == None:
        return    
    pi.hardware_PWM(BUZZ_GPIO, freq, 500000)
    tm.sleep(time)
    pi.hardware_PWM(BUZZ_GPIO, 0, 0)

def key1_pressed(gpio, level, tick):    
    #print(gpio, level, tick)
    if key1_func != None:
        key1_func()
	
def key2_pressed(gpio, level, tick):
    #print(gpio, level, tick)
    if key2_func != None:
        key2_func()
	
def key3_pressed(gpio, level, tick):
    #print(gpio, level, tick)
    if key3_func != None:
        key3_func()   


def init_buttons():
    if pi == None:
        return     
    global key1,key2,key3
    import pigpio
    pi.set_mode(KEY1_GPIO, pigpio.INPUT)
    pi.set_pull_up_down(KEY1_GPIO, pigpio.PUD_UP)
    pi.set_noise_filter(KEY1_GPIO, FILTER_STEADY, FILTER_ACTIVE)
    pi.set_mode(KEY2_GPIO, pigpio.INPUT)
    pi.set_pull_up_down(KEY2_GPIO, pigpio.PUD_UP)
    pi.set_noise_filter(KEY2_GPIO, FILTER_STEADY, FILTER_ACTIVE)
    pi.set_mode(KEY3_GPIO, pigpio.INPUT)
    pi.set_pull_up_down(KEY3_GPIO, pigpio.PUD_UP)
    pi.set_noise_filter(KEY3_GPIO, FILTER_STEADY, FILTER_ACTIVE)
    key1=pi.callback(KEY1_GPIO, pigpio.RISING_EDGE , key1_pressed)
    key2=pi.callback(KEY2_GPIO, pigpio.RISING_EDGE , key2_pressed)
    key3=pi.callback(KEY3_GPIO, pigpio.RISING_EDGE , key3_pressed)


ACTLD_DISABLE   = 0
ACTLD_MMC       = 1
ACTLD_FLASH     = 2
ACTLD_HEARTBEAT = 3
ACTLD_ON        = 4
ACTLD_OFF       = 5
def active_led(action):
    if pi == None:
        return     
    if action == ACTLD_DISABLE:
        os.system("echo none | sudo tee /sys/class/leds/ACT/trigger > null")
    elif action == ACTLD_MMC:
        os.system("echo mmc0 | sudo tee /sys/class/leds/ACT/trigger > null")
    elif action == ACTLD_FLASH:
        os.system("echo timer | sudo tee /sys/class/leds/ACT/trigger > null")
    elif action == ACTLD_HEARTBEAT:
        os.system("echo heartbeat | sudo tee /sys/class/leds/ACT/trigger > null")        
    elif action == ACTLD_ON:
        os.system("echo 1 | sudo tee /sys/class/leds/ACT/brightness > null")
    elif action == ACTLD_OFF:
        os.system("echo 0 | sudo tee /sys/class/leds/ACT/brightness > null")


if __name__ == '__main__':
    print("Start Tests")
    init()
    beep(1500)
    init_buttons()
    print("press a key for end")
    x=input()
    beep(1000)
    close()
    print("End...")      