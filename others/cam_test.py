from picamera import PiCamera,Color
from time import sleep

cam = PiCamera()

cam.rotation=-90
cam.annotate_text = " Hello world! "
cam.annotate_background = Color('blue')
cam.annotate_text_size = 30
cam.start_preview()
sleep(3)
for effect in cam.IMAGE_EFFECTS:
    cam.image_effect = effect
    cam.annotate_text = " Effect: %s " % effect
    sleep(2)
cam.stop_preview()
cam.close()

