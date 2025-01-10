import requests

#user:gkyr@yahoo.gr  pass:gkyr1234
#loc Nea Smyrni from google map
#37.938209123871076, 23.709251306382026

API_KEY = 'cc60f5942123b44409393d80500ce975'
LAT     = '37.93820'
LON     = '23.70925'

parameters = {'appid': API_KEY,
              'lat': LAT,'lon': LON,'units': 'metric','lang':'el'}

url = "https://api.openweathermap.org/data/2.5/weather"
#parameters['lat']='asdf'
data = requests.get(url, parameters).json()

print('-- Current ------------')
#print(data)
#print('----------------------')
print('Place: {} {}'.format(data['name'],data['sys']['country']))
print('{} ({})'.format(data['weather'][0]['description'],data['weather'][0]['id']))
print('Temperature: {} °C'.format(data['main']['temp']))
#print('Temp Limits: {}-{} °C'.format(data['main']['temp_min'],data['main']['temp_max']))
print('Feels Like : {} °C'.format(data['main']['feels_like']))
print('Humidity   : {} %'.format(data['main']['humidity']))
print('Pressure   : {} hPa'.format(data['main']['pressure']))
print('Wind       : {} m/s ({})'.format(data['wind']['speed'],data['wind']['deg']))
print('')


url = "https://api.openweathermap.org/data/2.5/forecast"
#parameters['lat']='asdf'
data = requests.get(url, parameters).json()

print('-- Forecast ------------')
#print(data)
#print('------------------------')
cnt = data['cnt']
#print('values: %d' %cnt)
for x in range(cnt):
    datetime = data['list'][x]['dt_txt']
    hour = datetime.split(' ')[1].split(':')[0]
    temper = float(data['list'][x]['main']['temp'])
    humid = data['list'][x]['main']['humidity']
    pressure = data['list'][x]['main']['pressure']
    id = data['list'][x]['weather'][0]['id']
    clouds = data['list'][x]['clouds']['all']
    wind = float(data['list'][x]['wind']['speed'])
    wind_dir = data['list'][x]['wind']['deg']
    if hour=='00':
        print()
    print('%s:  temp:%4.1f  humid:%2s  pressure:%4s  id:%3s  clouds:%3s%%  wind:%4.1f (%3s)' % (hour,temper,humid,pressure,id,clouds,wind,wind_dir))
