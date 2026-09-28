from gpiozero import  Button,PWMOutputDevice
import time

PIN=18
print('ititialize PWM!')


pin = PWMOutputDevice(PIN,frequency=50, initial_value=0.5)

key=input('press a key')
pin.off()
time.sleep(3)
pin.close()
time.sleep(3)
pin=Button(PIN)
print('wait press key1')
pin.wait_for_press()
print('End...')

