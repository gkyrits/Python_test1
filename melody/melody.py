import time as tm
from tone import *
import songbase as base

BUZZ_GPIO = 12
pi=None

VOL_MAX = 500000
VOL_LOW = 2000

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

def beep(freq=600, time=100):
    if pi == None:
        return
    delay=time/1000
    pi.hardware_PWM(BUZZ_GPIO, freq, VOL_LOW)
    tm.sleep(delay)
    pi.hardware_PWM(BUZZ_GPIO, 0, 0)


# demo melody, durations: 4 = quarter note, 8 = eighth note, etc.:
__melody = ( NOTE_C4, NOTE_G3, NOTE_G3, NOTE_A3, NOTE_G3, 0, NOTE_B3, NOTE_C4 )
__durations = ( 4, 8, 8, 4, 4, 4, 4, 4 )
demo_melody = ( __melody, __durations, "demo melody" )

def play_melody(melody):
    for idx in range(len(melody[0])):
        beep(melody[TONES][idx],1000/melody[DURACTIONS][idx])

def __next_action():
    print("1.next 2.play 3.exit")
    x = input()
    return x


if __name__ == '__main__':
    print("Start Tests")
    init()
    print("play ",demo_melody[NAME] ," ...")
    play_melody(demo_melody) 
    song_base = list(base.songs)
    for song in song_base:
        print("melody: ",song)
        act = __next_action()
        if act=='3':
            break
        elif act=='1':
            continue
        play_melody(base.songs[song])        
    close()
    print("End...")     