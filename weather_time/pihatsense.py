import time
import options as opt

info = {'Temperature':0.0, 'Humidity':0, 'Pressure_Temper':0.0, 'Pressure':0.0, 'Altitude':0.0, 'SeaPressure':0}
sea_pressure = 1015.0


def __estimate_altitude(pressure, seaPressure):
    # Simple barometric formula to estimate altitude
    if seaPressure <= 0:
        seaPressure = 1013.25  # standard sea level pressure
    return 44330.0 * (1.0 - (pressure / seaPressure) ** (1/5.255))


sense = None  # SenseHat object, created once


def __read_sensehat():
    global sense
    if sense is None:
        from sense_hat import SenseHat
        sense = SenseHat()
    info['Temperature'] = sense.get_temperature() + opt.SENSEHAT_TEMP_OFFSET
    info['Humidity'] = sense.get_humidity() + opt.SENSEHAT_HUMID_OFFSET
    info['Pressure_Temper'] = sense.get_temperature_from_pressure() + opt.SENSEHAT_PRESS_TEMP_OFFSET
    pressure = sense.get_pressure()
    if pressure <= 0:
        # pressure sensor returns 0 until it has a first sample, retry once
        time.sleep(0.5)
        pressure = sense.get_pressure()
    if pressure > 0:
        pressure += opt.SENSEHAT_PRESS_OFFSET
        info['Altitude'] = __estimate_altitude(pressure, sea_pressure)
    else:
        info['Altitude'] = 0.0  # no reading, formula would give 44330 m
    info['Pressure'] = pressure
    info['SeaPressure'] = sea_pressure


def set_sea_pressure(seaPress):
    global sea_pressure
    sea_pressure = seaPress


def exist():
    global sense
    if sense is None:
        try:
            from sense_hat import SenseHat
            sense = SenseHat()
            return True
        except:            
            return False
    else:
        return True


def get_sensor_info():
    try:
        __read_sensehat()
        return info
    except:
        info['Temperature']=0.0
        info['Humidity']=0
        info['Pressure_Temper']=0.0
        info['Pressure']=0.0
        info['Altitude']=0.0
        info['SeaPressure']=0
        return info

if __name__ == '__main__':
    while True:
        info = get_sensor_info()
        print('SeaPressure : {} hPa'.format(info['SeaPressure']))
        print('')
        print('Temperature  : {:.1f} °C'.format(info['Temperature']))
        print('Humidity     : {:.1f} %'.format(info['Humidity']))
        print('Press_Temper : {:.1f} °C'.format(info['Pressure_Temper']))
        print('Pressure     : {:.1f} hPa'.format(info['Pressure']))
        print('Altitude     : {:.1f} m'.format(info['Altitude']))
        print('')
        time.sleep(2)
