from gpiozero import PWMLED,PWMOutputDevice

print('ititialize PWM!')

pwm1 = PWMOutputDevice(18,frequency=4000, initial_value=0.5)
pwm2 = PWMOutputDevice(4, frequency=4000, initial_value=0.5)

key=input('press key...')
pwm1.off()
pwm2.off()
print('End...')

