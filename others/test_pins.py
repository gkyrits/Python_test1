from gpiozero import LED
from time import sleep

def test_gpio(led_id, cnt=20, delay=2) :
    print("test gpio %d" % led_id)
    tst_led = LED(led_id)
    x=0
    while x<cnt :
        print("cnt : %d" % x)
        x = x+1
        tst_led.on()
        sleep(2)
        tst_led.off()
        sleep(2)

x = input("GPIO for test ?")        
test_gpio(int(x))
print("end ...")
    
