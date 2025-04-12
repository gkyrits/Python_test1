import time as tm

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