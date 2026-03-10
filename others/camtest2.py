from picamera2 import Picamera2, Preview
import time

#Picamera2.set_logging(Picamera2.CRITICAL)

#print a dictionary list
def pprint(obj, indent=0):
    """Pretty-print a dictionary, list, or nested structure to the console."""
    space = ' ' * indent
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{space}{key}:", end=' ')
            if isinstance(value, (dict, list)):
                print()
                pprint(value, indent + 2)
            else:
                print(value)
    elif isinstance(obj, list):
        for i, item in enumerate(obj, start=1):
            print(f"{space}[{i}]")
            pprint(item, indent + 2)
    else:
        print(space + str(obj))


print("===== Camera info: ====\n")
pprint(Picamera2.global_camera_info())
print("\n=====================\n")
print("\n")

picam = Picamera2(2)

print("===== Camera Properties: ====\n")
pprint(picam.camera_properties)
print("\n=====================\n")
print("\n")

print("===== Sensor Modes: ====\n")
pprint(picam.sensor_modes)
print("\n=====================\n")
print("\n")

config = picam.create_preview_configuration()
#print(config)
#config = picam.create_preview_configuration({"format": "YUYV"})
picam.configure(config)
picam.start_preview(Preview.QT, x=0, y=0, width=320, height=240)
picam.start()
time.sleep(20)
#picam.capture_file("test.jpg")
