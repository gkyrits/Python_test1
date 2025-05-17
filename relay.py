from gpiozero import LED
from time import sleep

red = LED(4)
cnt=0
wait_tm=40
charg_tm=0

while True:
    print("")
    print("charge no:"+str(cnt))
    print("charge time:"+str(charg_tm))
    cnt+=1
    charg_tm=cnt*wait_tm
    red.on()
    sleep(wait_tm)
    red.off()
    sleep(1)