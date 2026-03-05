import pigpio as gp

pwm_pin = 18

print('initialize pwm with pigpio')
pwm1 = gp.pi()
pwm1.set_mode(pwm_pin,gp.OUTPUT)
pwm1.hardware_PWM(pwm_pin,1000000,50*10000)

k=input('press a key!')
pwm1.hardware_PWM(pwm_pin,0,0)
pwm1.stop()
print('End..')
