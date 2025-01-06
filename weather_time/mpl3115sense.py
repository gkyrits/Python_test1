## gkyr:modified from MPL3115A2.py

#import smbus
import time

info = {'Temperature':0.0, 'Pressure':0.0, 'Altitude':0.0}

# MPL3115A2 address, 0x60(96)

def __read_mpl3115():
    import smbus
    bus = smbus.SMBus(1)
		
	# Select control register, 0x26(38)
	#		0xB9(185)	Active mode, OSR = 128, Altimeter mode
    bus.write_byte_data(0x60, 0x26, 0xB9)
	# MPL3115A2 address, 0x60(96)
	# Select data configuration register, 0x13(19)
	#		0x07(07)	Data ready event enabled for altitude, pressure, temperature
    bus.write_byte_data(0x60, 0x13, 0x07)
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
    #print("Temperature : %.1f C" %cTemp)
    #print("Pressure    : %.1f hPa" %pressure)
    #print("Altitude    : %.1f m" %altitude)
	#print("Temperature in Fahrenheit  : %.2f F" %fTemp)
    info['Temperature']=cTemp
    info['Pressure']=pressure
    info['Altitude']=altitude


def get_sensor_info():
    try:
        __read_mpl3115()
        return info
    except:
        info['Temperature']=0.0
        info['Pressure']=0.0
        info['Altitude']=0.0
        return info
    
if __name__ == '__main__':
    while True:
        info = get_sensor_info()
        print('Temperature : {:.1f} °C'.format(info['Temperature']))
        print('Pressure    : {:.1f} hPa'.format(info['Pressure']))
        print('Altitude    : {:.1f} m'.format(info['Altitude']))
        print('')
        time.sleep(2)