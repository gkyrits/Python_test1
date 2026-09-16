import time

info = {'Temperature':0.0, 'Humidity':0, 'Pressure':0.0, 'Altitude':0.0, 'SeaPressure':0}
sea_pressure = 1015.0


def __estimate_altitude(pressure, seaPressure):
    # Simple barometric formula to estimate altitude
    return 44330.0 * (1.0 - (pressure / seaPressure) ** (1/5.255))


def __read_sensehat():
    from sense_hat import SenseHat
    sense = SenseHat()
    info['Temperature'] = sense.get_temperature()
    info['Humidity'] = sense.get_humidity()
    info['Pressure'] = sense.get_pressure()
    info['Altitude'] = __estimate_altitude(info['Pressure'], sea_pressure)
    info['SeaPressure'] = sea_pressure


def set_sea_pressure(seaPress):
    global sea_pressure
    sea_pressure = seaPress


def get_sensor_info():
    try:
        __read_sensehat()
        return info
    except:
        info['Temperature']=0.0
        info['Humidity']=0
        info['Pressure']=0.0
        info['Altitude']=0.0
        info['SeaPressure']=0
        return info

if __name__ == '__main__':
    while True:
        info = get_sensor_info()
        print('SeaPressure : {} hPa'.format(info['SeaPressure']))
        print('')
        print('Temperature : {:.1f} °C'.format(info['Temperature']))
        print('Humidity    : {} %'.format(info['Humidity']))
        print('Pressure    : {:.1f} hPa'.format(info['Pressure']))
        print('Altitude    : {:.1f} m'.format(info['Altitude']))
        print('')
        time.sleep(2)
