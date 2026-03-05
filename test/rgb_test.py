from gpiozero import LED,RGBLED,Buzzer,TonalBuzzer
from gpiozero.tones import Tone
#from colorzero import Color
from time import sleep

led = RGBLED(red=29, green=28, blue=30)
bz = Buzzer(31)
tn = TonalBuzzer(25)
#ld = LED(25)

TIME=4.0
MAX_RED=100
MAX_GREEN=100
MAX_BLUE=100

red_wait=TIME/MAX_RED
green_wait=TIME/MAX_GREEN
blue_wait=TIME/MAX_BLUE

def red_play() :
    for rx in range(0,MAX_RED,1) :
        r = rx / 100.0
        print("rx=%d red=%.2f" % (rx,r))
        led.red=r
        sleep(red_wait)
    led.red=1
    sleep(0.1)
    for rx in range(MAX_RED,0,-1) :
        r = rx / 100.0
        print("rx=%d red=%.2f" % (rx,r))
        led.red=r
        sleep(red_wait)
        led.red=0

def green_play() :
    for rx in range(0,MAX_GREEN,1) :
        r = rx / 100.0
        print("rx=%d green=%.2f" % (rx,r))
        led.green=r
        sleep(green_wait)
    led.green=1
    sleep(0.1)
    for rx in range(MAX_GREEN,0,-1) :
        r = rx / 100.0
        print("rx=%d green=%.2f" % (rx,r))
        led.green=r
        sleep(green_wait)
        led.green=0

def blue_play() :
    for rx in range(0,MAX_BLUE,1) :
        r = rx / 100.0
        print("rx=%d blue=%.2f" % (rx,r))
        led.blue=r
        sleep(blue_wait)
    led.blue=1
    sleep(0.1)
    for rx in range(MAX_BLUE,0,-1) :
        r = rx / 100.0
        print("rx=%d blue=%.2f" % (rx,r))
        led.blue=r
        sleep(blue_wait)
        led.blue=0

def color_play() :
	for rx in range(0,MAX_RED,MAX_RED//10) :
		r = rx / 100.0
		print("rx=%d red=%.2f ---" % (rx,r))
		led.red=r
		#sleep(red_wait)
		for gx in range(0,MAX_GREEN,MAX_GREEN//10) :
			g = gx / 100.0
			print("gx=%d green=%.2f -" % (gx,g))
			led.green=g
			#sleep(green_wait)
			for bx in range(0,MAX_BLUE,MAX_BLUE//10) :
				b = bx / 100.0
				print("bx=%d blue=%.2f" % (bx,b))
				led.blue=b
				sleep(blue_wait)

def play_tone() :
    tn.play("A3")
    sleep(0.1)
    tn.play("A4")
    sleep(0.1)
    tn.play("A5")
    sleep(0.1)
    tn.stop()

def demo_tone() :
    for note in 'C4 D4 E4 F4 G4 A4 B4 C5'.split() :
        tone = Tone(note)
        print(repr(tone))
        tn.play(tone)
        sleep(0.3)
        tn.stop()


def play_freq() :
    for n in range(0,10000,1) :
        ld.toggle()


def play_buzzer() :
    bz.beep(0.05,0,1)

def play_all() :
    #play_buzzer()
    #play_freq()
    play_tone()
    #demo_tone()
    led.color=(0,0,0)
    red_play()
    play_buzzer()
    green_play()
    play_buzzer()
    blue_play()
    play_buzzer()
    led.color=(0,0,0)
    color_play()



while True :
    play_all()


