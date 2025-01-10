import weather as whr

def print_weather(info):
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
        print('Wind       : {} m/s ({})'.format(info['Wind'],info['WindDeg']))
    print('') 

def print_forecast(info):
    print('')
    if info['Error'] != '':
        print('Error: ' + info['Error'])
    else:
        item_cnt=info['Items']
        for x in range(item_cnt):
            if info['List'][x]['Hour']=='00':
                print()
            print('Date:%s  Hour:%s' % (
                info['List'][x]['Date'],
                info['List'][x]['Hour'],
                ))
    print('')

print('meteosource info:')
print_weather(whr.get_weather_info(source='meteo'))
print('openweather info:')
print_weather(whr.get_weather_info())
print('openweather forecast:')
print_forecast(whr.get_forecast_info())


