from sense_hat import SenseHat

sense = SenseHat()

def read_sensors():
    print("\n")
    pressure = sense.get_pressure()
    print("Pressure: %d Millibars" % pressure)
    humidity = sense.get_humidity()
    print("Humidity: %.1f %%rH" % humidity)
    temp = sense.get_temperature()
    print("Temperature: %.1f C" % temp)
    temp = sense.get_temperature_from_humidity()
    print("Hum Temperature: %.1f C" % temp)
    temp = sense.get_temperature_from_pressure()
    print("Pre Temperature: %.1f C" % temp)

for i in range(1000) :
    print("\nloop %d:" % i)
    sense.show_message("Loop:", text_colour=[128, 128, 0])
    sense.show_message("%d" % i, text_colour=[128, 0, 128])
    sense.show_message("Hello world!", text_colour=[128, 0, 0])
    read_sensors()
    sense.show_message("Hello world!", text_colour=[0, 128, 0])
    read_sensors()
    sense.show_message("Hello world!", text_colour=[0, 0, 128])
    read_sensors()

sense.clear()
print("end")
