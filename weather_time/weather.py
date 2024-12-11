import requests

#user:gkyr@yahoo.gr  pass:gkyr1234
#loc Nea Smyrni from google map
#37.938209123871076, 23.709251306382026

#---openweather
OPEN_API_KEY = 'cc60f5942123b44409393d80500ce975'
open_param = {'appid': OPEN_API_KEY,
              'lat': '37.93820','lon': '23.70925','units': 'metric','lang':'el'}
open_url = 'https://api.openweathermap.org/data/2.5/weather'

#---meteosource
METEO_API_KEY = '8r3xztnjqi6uj9vqu11dg6wxnzoowpts066hr9s1'
meteo_param = {'key': METEO_API_KEY,
              'lat': '37.93820','lon': '23.70925'}
meteo_place_url = "https://www.meteosource.com/api/v1/free/nearest_place"
meteo_point_url = 'https://www.meteosource.com/api/v1/free/point'

#---return info
info = {'Place':'', 'Descript':'', 'Temper':0.0, 'Like':0.0, 'Humidity':0, 'Pressure':0, 'Wind':0.0, 'WindDeg':0, 'Clouds':0, 'Id':0, 'Error':''}


def get_meteo_weather_info(lat, lon):    
    open_param['lat']=lat
    open_param['lon']=lon
    try:
        data_place = requests.get(meteo_place_url, meteo_param).json()
        data_point = requests.get(meteo_point_url, meteo_param).json()
    except:
        info['Error']='request exception'    
        return info
    info['Place']=data_place['name']+' '+data_place['country']
    info['Descript']=data_point['current']['summary']
    info['Temper']=data_point['current']['temperature']
    info['Like']='-'
    info['Humidity']='-'
    info['Pressure']='-'
    info['Wind']='-'
    info['WindDeg']='-'
    info['Clouds']='-'
    info['Id']=0
    return info



def get_open_weather_info(lat, lon):    
    open_param['lat']=lat
    open_param['lon']=lon
    try:
        data = requests.get(open_url, open_param).json()
    except:
        info['Error']='request exception'    
        return info
    if data['cod'] != 200:
        info['Error']=data['message']
        return info
    info['Place']=data['name']+' '+data['sys']['country']
    info['Descript']=data['weather'][0]['description']
    info['Temper']=data['main']['temp']
    info['Like']=data['main']['feels_like']
    info['Humidity']=data['main']['humidity']
    info['Pressure']=data['main']['pressure']
    info['Wind']=data['wind']['speed']
    info['WindDeg']=data['wind']['deg']
    info['Clouds']=data['clouds']['all']
    info['Id']=data['weather'][0]['id']
    return info




def get_weather_info(lat='37.93820', lon='23.70925', source='open'):
    if source=='open':
        return get_open_weather_info(lat,lon)
    else:
        return get_meteo_weather_info(lat,lon)




if __name__ == '__main__':
    info = get_weather_info()
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
        print('Clouds     : {} %'.format(info['Clouds']))
        print('Wind       : {} m/s'.format(info['Wind']))
        print('Wind Deg   : {} m/s'.format(info['WindDeg']))
    print('')    
