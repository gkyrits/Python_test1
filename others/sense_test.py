from sense_hat import SenseHat

sense = SenseHat()

def read_sensors():
    pressure = sense.get_pressure()
    sense.show_message("P: %d" % pressure, text_colour=[0, 0, 128])
    
    temp = sense.get_temperature()  
    sense.show_message("T: %.1f" % temp, text_colour=[128, 0, 0])
    
    humidity = sense.get_humidity()
    sense.show_message("H: %.1f" % humidity, text_colour=[0, 128, 0])


while True :
    read_sensors()

sense.clear()