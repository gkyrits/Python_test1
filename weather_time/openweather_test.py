import requests

#user:gkyr@yahoo.gr  pass:gkyr1234
#loc Nea Smyrni from google map
#37.938209123871076, 23.709251306382026

API_KEY = 'cc60f5942123b44409393d80500ce975'

parameters = {'appid': API_KEY,
              'lat': '37.93820','lon': '23.70925','units': 'metric','lang':'el'}

url = "https://api.openweathermap.org/data/2.5/weather"
#parameters['lat']='asdf'
data = requests.get(url, parameters).json()

print('--------------')
print(data)
print('--------------')
print('Place: {} {}'.format(data['name'],data['sys']['country']))
print('{} ({})'.format(data['weather'][0]['description'],data['weather'][0]['id']))
print('Temperature: {} °C'.format(data['main']['temp']))
print('Feels Like : {} °C'.format(data['main']['feels_like']))
print('Humidity   : {} %'.format(data['main']['humidity']))
print('Pressure   : {} hPa'.format(data['main']['pressure']))
print('Wind       : {} m/s ({})'.format(data['wind']['speed'],data['wind']['deg']))
print('')
