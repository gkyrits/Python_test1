import time
import os

FILE = 'sensor'  # file name to save info

info = {'sens1': {}, 'sens2': {}, 'sens3': {}}

# get year_month string
def __get_year_month():
    return time.strftime('%Y-%m', time.localtime())

# get current year string
def __get_year():
    return time.strftime('%Y', time.localtime())

# key mapping for renaming
key_mapping = {
    'Temperature': 'Temper',
    'Humidity': 'Humid',
    'Pressure': 'Press',
    'Altitude': 'Altit',
    'SeaPressure': 'SeaPress'
}

# format floats in the dictionary to 1 decimal point and rename keys
def __format_data(data):
    if isinstance(data, dict):
        return {key_mapping.get(k, k): __format_data(v) for k, v in data.items()}
    elif isinstance(data, float):
        return f"{data:.1f}"
    elif isinstance(data, list):
        return [__format_data(i) for i in data]
    else:
        return data

# save info with timestamp to file in a line
def save_info():
    try:
        formatted_info = __format_data(info)
        year = __get_year()
        directory = os.path.join('repository', year)
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, FILE + '-' + __get_year_month())
        with open(file_path, 'a') as f:
            f.write(time.strftime('%d %H:%M:%S', time.localtime()) + ' ')
            f.write(str(formatted_info) + '\n')
    except Exception as e:
        print('Fail to save info to file:', e)



repo_info = {'day':'0', 'time':'0:0:0', 'info':{}}

#load file return as a list of repo_info
def load_info():
    try:
        year = __get_year()
        directory = os.path.join('repository', year)
        os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, FILE + '-' + __get_year_month())
        with open(file_path, 'r') as f:
            lines = f.readlines()
            repo_info_list = []
            for line in lines:
                line = line.strip()
                day_str, time_str, info_str = line.split(' ', 2)
                repo_info_list.append({'day': day_str, 'time': time_str, 'info': eval(info_str)})
            return repo_info_list
    except Exception as e:
        print('Fail to load info from file:', e)
        return []


#load repo_info until X hours before, return as a list of repo_info, open more files if needed

    
#test load_info()
if __name__ == '__main__':
    print(load_info())






    






