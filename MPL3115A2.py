# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# MPL3115A2
# This code is designed to work with the MPL3115A2_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/products

import smbus
import time

# Get I2C bus
bus = smbus.SMBus(1)

# MPL3115A2 address, 0x60(96)

def read_mpl3115():
	# Select control register, 0x26(38)
	#		0xB9(185)	Active mode, OSR = 128, Altimeter mode
	bus.write_byte_data(0x60, 0x26, 0xB9)
	# MPL3115A2 address, 0x60(96)
	# Select data configuration register, 0x13(19)
	#		0x07(07)	Data ready event enabled for altitude, pressure, temperature
	bus.write_byte_data(0x60, 0x13, 0x07)

	# read Sea level pressure
	#bus.write_byte_data(0x60,0x14,0xC7)
	#bus.write_byte_data(0x60,0x15,0x6A)

	data = bus.read_i2c_block_data(0x60, 0x14, 2)
	sea_press= ((data[0]*256 + data[1]) *2) /100
	print('User Sea Pressure : %d ' %sea_press)
	print('')


	# MPL3115A2 address, 0x60(96)
	# Select control register, 0x26(38)
	#		0xB9(185)	Active mode, OSR = 128, Altimeter mode
	bus.write_byte_data(0x60, 0x26, 0xB9)
	time.sleep(1)

	# MPL3115A2 address, 0x60(96)
	# Read data back from 0x00(00), 6 bytes
	# status, tHeight MSB1, tHeight MSB, tHeight LSB, temp MSB, temp LSB
	data = bus.read_i2c_block_data(0x60, 0x00, 6)
	# Convert the data to 20-bits
	tHeight = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
	temp = ((data[4] * 256) + (data[5] & 0xF0)) / 16
	altitude = tHeight / 16.0
	if altitude>32767 :
		altitude=altitude-65535
	cTemp = temp / 16.0
	#fTemp = cTemp * 1.8 + 32

	# MPL3115A2 address, 0x60(96)
	# Select control register, 0x26(38)
	#		0x39(57)	Active mode, OSR = 128, Barometer mode
	bus.write_byte_data(0x60, 0x26, 0x39)
	time.sleep(1)

	# MPL3115A2 address, 0x60(96)
	# Read data back from 0x00(00), 4 bytes
	# status, pres MSB1, pres MSB, pres LSB
	data = bus.read_i2c_block_data(0x60, 0x00, 4)
	# Convert the data to 20-bits
	pres = ((data[1] * 65536) + (data[2] * 256) + (data[3] & 0xF0)) / 16
	pressure = (pres / 4.0) / 100.0

	# Output data to screen
	print("Temperature : %.1f C" %cTemp)
	print("Pressure    : %.1f hPa" %pressure)
	print("Altitude    : %.1f m" %altitude)
	#print("Temperature in Fahrenheit  : %.2f F" %fTemp)

def set_sea_level(sea_press):
	sea_level = int((sea_press * 100) /2)
	data = list(sea_level.to_bytes(2,byteorder='big'))
	bus.write_i2c_block_data(0x60,0x14,data)

set_sea_level(1022)
while True:
    read_mpl3115()
    print("")
    time.sleep(10)
