## gkyr:modified from SI7021.py

#import smbus
import time

info = {'Temperature':0.0, 'Humidity':0.0}

# SI7021 address, 0x40(64)

def __read_SI7021():
    import smbus
    bus = smbus.SMBus(1)

	# Read data, 2 bytes, Humidity MSB first
    rh = bus.read_i2c_block_data(0x40, 0xE5, 2) 
	#what really happens here is that master sends a 0xE5 command (measure RH, hold master mode) and read 2 bytes back
	#if you read 3 bytes the last one is the CRC!
    time.sleep(0.1)
	# Convert the data
    humidity = ((rh[0] * 256 + rh[1]) * 125 / 65536.0) - 6

	# SI7021 address, 0x40(64)
	# Read data , 2 bytes, Temperature MSB first
    temp = bus.read_i2c_block_data(0x40, 0xE3,2)
	#what really happens here is that master sends a 0xE3 command (measure temperature, hold master mode) and read 2 bytes back 
	#if you read 3 bytes the last one is the CRC!
    time.sleep(0.1)
	# Convert the data
    cTemp = ((temp[0] * 256 + temp[1]) * 175.72 / 65536.0) - 46.85
	#fTemp = cTemp * 1.8 + 32

	# Output data to screen
    #print ("Temperature  : %.1f°C" %cTemp)
    #print ("Humidity %%RH : %.1f%%" %humidity)	
	#print ("Temperature Fahrenheit: %.2f°F" %fTemp)    
    info['Temperature']=cTemp
    info['Humidity']=humidity

def get_sensor_info():
    try:
        __read_SI7021()
        return info
    except:
        info['Temperature']=0.0
        info['Humidity']=0.0
        return info
    
if __name__ == '__main__':
    while True:
        info = get_sensor_info()
        print('Temperature : {:.1f} °C'.format(info['Temperature']))
        print('Humidity    : {} %'.format(info['Humidity']))
        print('')
        time.sleep(2)