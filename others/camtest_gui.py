from picamera2 import Picamera2, Preview
import time

print("**Camera info:**\n")
print(Picamera2.global_camera_info())
print("\n")

picam2 = Picamera2(0)
config = picam2.create_preview_configuration()
#config = picam2.create_preview_configuration({"format": "YUYV"})
picam2.configure(config)
picam2.start_preview(Preview.QT, x=0, y=0, width=320, height=240)
picam2.start()
time.sleep(20)
#picam2.capture_file("test.jpg")
