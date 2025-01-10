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
    #print('')
    if info['Error'] != '':
        print('Error: ' + info['Error'])
    else:
        item_cnt=info['Items']
        for x in range(item_cnt):
            if (info['List'][x]['Hour']=='00') or (x==0):
                print()
                print('Date:%s' % info['List'][x]['Date'])
            print('Hour:%s Temp:%4.1f humid:%2s press:%4s id:%3s clouds:%3s%% wind:%4.1f (%3s)' % (
                info['List'][x]['Hour'],
                info['List'][x]['Temper'],
                info['List'][x]['Humidity'],
                info['List'][x]['Pressure'],
                info['List'][x]['Id'],
                info['List'][x]['Clouds'],
                info['List'][x]['Wind'],
                info['List'][x]['WindDeg'],
                ))
    print('')

print('meteosource info:')
print_weather(whr.get_weather_info(source='meteo'))
print('openweather info:')
print_weather(whr.get_weather_info())
print('openweather forecast:')
print_forecast(whr.get_forecast_info())


