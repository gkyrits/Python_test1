import requests

#user:gkyr@yahoo.gr  pass:gkyr1234
#loc Nea Smyrni from google map
#37.938209123871076, 23.709251306382026

API_KEY = '8r3xztnjqi6uj9vqu11dg6wxnzoowpts066hr9s1'

parameters = {'key': API_KEY,
              'lat': '37.93820','lon': '23.70925'}

url = "https://www.meteosource.com/api/v1/free/nearest_place"
data = requests.get(url, parameters).json()
place = data['name']
print('')
print('Place :{}, {}, {}'.format(data['name'],data['adm_area2'],data['country']))

url = "https://www.meteosource.com/api/v1/free/point"
data = requests.get(url, parameters).json()
print(data['current']['summary'])
print('Temperature {} °C'.format(data['current']['temperature']))
print('')
#print('--------------')
#print(data)
