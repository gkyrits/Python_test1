
import requests

#loc from google map
#37.938209123871076, 23.709251306382026

parameters = {'key': '8r3xztnjqi6uj9vqu11dg6wxnzoowpts066hr9s1',
              'lat': '37.93820','lon': '23.70925'}

url = "https://www.meteosource.com/api/v1/free/nearest_place"
data = requests.get(url, parameters).json()
place = data['name']

url = "https://www.meteosource.com/api/v1/free/point"
data = requests.get(url, parameters).json()
print('Current temperature in {} is {} °C.'.format(place,data['current']['temperature']))  
