from gpiozero import TonalBuzzer
from gpiozero.tones import Tone 
from gpiozero import PWMOutputDevice as pwm
from gpiozero import Button
import time as tm

BUZZ_GPIO = 12
KEY1_GPIO = 18
KEY2_GPIO = 17
KEY3_GPIO = 5

def test_buzzer():
	bz = TonalBuzzer(BUZZ_GPIO)
	tone=300
	while True:
		bz.play(tone)
		print("play "+str(tone))
		tm.sleep(.2)
		tone+=100
		if tone>800:
			break	
	bz.stop()

def test_buzzer_freq(freq):
	bz=TonalBuzzer(BUZZ_GPIO)
	tone=Tone(frequency=freq)
	bz.play(tone)
	tm.sleep(.5)
	bz.stop()
	
def test_buzzer_pwm():
	bz=pwm(BUZZ_GPIO)
	freq=100
	bz.frequency=freq
	bz.value=.5
	while True:
		#print("play "+str(freq))
		tm.sleep(.1)
		freq+=100
		bz.frequency=freq
		if freq>3000:
			break
	bz.off()
	
def beep_pwm(freq=600, time=.1):
	bz=pwm(BUZZ_GPIO)
	bz.frequency=freq
	bz.value=.5
	tm.sleep(time)
	bz.off()	
	
def key1_pressed():
	beep_pwm()
	print("Key1 pressed")
	
def key2_pressed():
	beep_pwm()
	print("Key2 pressed")
	
def key3_pressed():
	beep_pwm()
	print("Key3 pressed")		
	
def test_buttons():
	global key1,key2,key3
	key1=Button(KEY1_GPIO)
	key2=Button(KEY2_GPIO)
	key3=Button(KEY3_GPIO) 
	key1.when_released = key1_pressed
	key2.when_released = key2_pressed
	key3.when_released = key3_pressed
	

if __name__ == '__main__':
	print("Start Tests")
	#------
	test_buttons()
	#test_buzzer()	
	#test_buzzer_freq(550)
	test_buzzer_pwm()
	#-----
	print("press a key for end")
	x=input()
	print("End...")

