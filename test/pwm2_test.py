import RPi.GPIO as gp

pin = 12

print('initialize with RPi')
gp.setmode(gp.BOARD)
gp.setup(pin,gp.OUT)
pwm1 = gp.PWM(pin,4000)
pwm1.start(50)

k=input('press a key')
pwm1.stop()
print('End...')


