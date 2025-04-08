import pigpio
import time as tm

BUZZ_GPIO = 12
KEY1_GPIO = 18
KEY2_GPIO = 17
KEY3_GPIO = 5

pi=None
key1=None
key2=None
key3=None

def init_gpio():
    global pi
    pi=pigpio.pi()

def close_gpio():
    if pi == None:
        return        
    pi.stop()

def test_buzzer_pwm():
    if pi == None:
        return    
    freq=100
    while True:
        #print("play "+str(freq))
        pi.hardware_PWM(BUZZ_GPIO, freq, 500000)
        tm.sleep(.1)
        freq+=100
        pi.hardware_PWM(BUZZ_GPIO, freq, 500000)
        if freq>3000:
            break
    pi.hardware_PWM(BUZZ_GPIO, 0, 0)


def beep_pwm(freq=600, time=.1):
    if pi == None:
        return    
    pi.hardware_PWM(BUZZ_GPIO, freq, 500000)
    tm.sleep(time)
    pi.hardware_PWM(BUZZ_GPIO, 0, 0)


def key1_pressed(gpio, level, tick):
    beep_pwm(300)
    print("Key1 pressed:")
    print(gpio, level, tick)
    print("")
	
def key2_pressed(gpio, level, tick):
    beep_pwm(400)
    print("Key2 pressed:")
    print(gpio, level, tick)
    print("")
	
def key3_pressed(gpio, level, tick):
    beep_pwm(500)
    print("Key3 pressed:")
    print(gpio, level, tick)
    print("")
	
def test_buttons():
    global key1,key2,key3
    pi.set_mode(KEY1_GPIO, pigpio.INPUT)
    pi.set_pull_up_down(KEY1_GPIO, pigpio.PUD_UP)
    pi.set_noise_filter(KEY1_GPIO, 10000, 0)

    pi.set_mode(KEY2_GPIO, pigpio.INPUT)
    pi.set_pull_up_down(KEY2_GPIO, pigpio.PUD_UP)
    pi.set_noise_filter(KEY2_GPIO, 10000, 0)

    pi.set_mode(KEY3_GPIO, pigpio.INPUT)
    pi.set_pull_up_down(KEY3_GPIO, pigpio.PUD_UP)
    pi.set_noise_filter(KEY3_GPIO, 10000, 0)

    key1=pi.callback(KEY1_GPIO, pigpio.FALLING_EDGE, key1_pressed)
    key2=pi.callback(KEY2_GPIO, pigpio.FALLING_EDGE, key2_pressed)
    key3=pi.callback(KEY3_GPIO, pigpio.FALLING_EDGE, key3_pressed)


if __name__ == '__main__':
    print("Start Tests")
    init_gpio()
    #-----
    test_buttons()
    #beep_pwm()
    #test_buzzer_pwm()
    #-----
    print("press a key for end")
    x=input()
    beep_pwm(1000)
    close_gpio()
    print("End...")    




