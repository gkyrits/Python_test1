## gkyr:modified from AHT10.py

#import smbus
import time

info = {'Temperature':0.0, 'Humidity':0.0}

def __read_ATH10():
    import smbus    
    # Get I2C bus
    #bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
    bus = smbus.SMBus(1)   # Rev 2 Pi uses 1
    # when you have a 121 IO Error, uncomment the next pause
    # time.sleep(1) #wait here to avoid 121 IO Error    
    config = [0x08, 0x00]    
    bus.write_i2c_block_data(0x38, 0xE1, config)
    time.sleep(0.5)
    byt = bus.read_byte(0x38)
    #print(byt&0x68)
    MeasureCmd = [0x33, 0x00]
    bus.write_i2c_block_data(0x38, 0xAC, MeasureCmd)
    time.sleep(0.5)
    data = bus.read_i2c_block_data(0x38,0x00)
    #print(data)
    temp = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
    ctemp = ((temp*200) / 1048576) - 50
    #print(u'Temperature  : {0:.1f}°C'.format(ctemp))
    info['Temperature']=ctemp
    tmp = ((data[1] << 16) | (data[2] << 8) | data[3]) >> 4
    #print(tmp)
    chumid = int(tmp * 100 / 1048576)
    #print(u'Humidity %RH : {0:.1f}%'.format(chumid))
    info['Humidity']=chumid

def get_sensor_info():
    try:
        __read_ATH10()
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
