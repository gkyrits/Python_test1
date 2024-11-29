import weather as whr

def print_info(info):
    print('')
    if info['Error'] != '':
        print('Error: '+info['Error'])
    else:
        print('Place: '+info['Place'])
        print('{} ({})'.format(info['Descript'],(info['Id'])))
        print('Temperature: {} °C'.format(info['Temper']))
        print('Feels Like : {} °C'.format(info['Like']))
        print('Humidity   : {} %'.format(info['Humidity']))
        print('Pressure   : {} hPa'.format(info['Pressure']))
        print('Wind       : {} m/s'.format(info['Wind']))
    print('') 


print('openweather info:')
print_info(whr.get_weather_info())
print('meteosource info:')
print_info(whr.get_weather_info(source='meteo'))

