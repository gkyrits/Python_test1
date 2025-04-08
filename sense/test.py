from sense_hat import SenseHat
from time import sleep

LED_LUM	= 100

sense = SenseHat()
sense.set_rotation(90)


def get_mesures():
	print("")
	temp = sense.get_temperature_from_humidity()
	print("Temperature (Hum): {:.1f} C".format(temp))
	temp = sense.get_temperature_from_pressure()
	print("Temperature (Press): {:.1f} C".format(temp))	
	humidity = sense.get_humidity()
	print("Humidity: {:.1f} %rH".format(humidity))
	pressure = sense.get_pressure()
	print("Pressure: {:.1f} Millibars".format(pressure))
	
	
def get_joystick():
	print("wait Press joysticK!")
	event = sense.stick.wait_for_event()
	print("The joystick was {} {}".format(event.action, event.direction))
	sleep(0.1)
	event = sense.stick.wait_for_event()
	print("The joystick was {} {}".format(event.action, event.direction))			


while True:
	print("")
	get_mesures()
	sense.show_message("Hello RED world!", text_colour=[LED_LUM, 0, 0])
	get_mesures()
	sense.show_message("Hello GREEN world!", text_colour=[0, LED_LUM, 0])
	get_mesures()
	sense.show_message("Hello BLUE world!", text_colour=[0, 0, LED_LUM])
	get_mesures()


	
