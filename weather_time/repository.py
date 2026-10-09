import struct
import ast
import time
import os
import pihatsense
import options as opt

FILE = 'sensor'  # file name to save info
# directory to save info, next to this module so every process (sensor_server,
# raspi_play, graphs) uses the same one whatever the working directory
DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repository')

USE_PI_SENSE_HAT = 1 if pihatsense.exist() else 0  # auto detect Sense HAT

info = {'sens1': {}, 'sens2': {}, 'sens3': {}, 'sens4': {}, 'web': {}}

# get year_month string
def __get_year_month():
    return time.strftime('%Y-%m', time.localtime())

# get current year string
def __get_year():
    return time.strftime('%Y', time.localtime())

# get epoch time from year, month, day, hour, minute
def get_epoch(year, month, day, hour, minute):
    # Create a struct_time object
    time_tuple = (year, month, day, hour, minute, 0, 0, 0, -1)
    # Convert to epoch time
    epoch_time = time.mktime(time_tuple)
    return epoch_time

# key mapping for renaming
key_mapping = {
    'sens1' : 's1',
    'sens2' : 's2',
    'sens3' : 's3',
    'sens4' : 's4',
    'web' : 'w',
    'Temperature': 'T',
    'Humidity': 'H',
    'Pressure': 'P',
    'Altitude': 'A',
    'SeaPressure': 'S'
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
        #year = __get_year()
        #directory = os.path.join('repository', year)
        os.makedirs(DIR, exist_ok=True)
        file_path = os.path.join(DIR, FILE + '-' + __get_year_month())
        with open(file_path, 'a') as f:
            f.write(time.strftime('%d %H:%M:%S', time.localtime()) + ' ')
            f.write(str(formatted_info) + '\n')
    except Exception as e:
        print('Fail to save info to file:', e)


RECID = 0xEE

# value*scale as int, clamped so a bad sensor reading can't break the record
def __short(val, scale=10):
    return max(-32768, min(32767, int(val * scale)))

def __byte(val):
    return max(0, min(255, int(val))).to_bytes(1, 'big')

# save info with timestamp to file in a binary using struct
def save_info_binary():
    try:
        os.makedirs(DIR, exist_ok=True)
        file_path = os.path.join(DIR, FILE + '-' + __get_year_month() + '.bin')
        time_str = time.strftime('%d %H %M %S', time.localtime())
        time_parts = time_str.split(' ')
        #build the whole record first, so a failure never writes half a record
        rec = struct.pack('ccccc', RECID.to_bytes(1, 'big'),
                          __byte(time_parts[0]), __byte(time_parts[1]),
                          __byte(time_parts[2]), __byte(time_parts[3]))
        #record layout is fixed, a disabled sensor (options SENSEx_EN=0) is saved as zeros
        #sensor1
        if opt.SENSE1_EN:
            sens1 = info['sens4'] if USE_PI_SENSE_HAT else info['sens1']
            rec += struct.pack('hc', __short(sens1['Temperature']), __byte(sens1['Humidity']))
        else:
            rec += struct.pack('hc', 0, __byte(0))
        #sensor2
        if opt.SENSE2_EN:
            rec += struct.pack('hc', __short(info['sens2']['Temperature']), __byte(info['sens2']['Humidity']))
        else:
            rec += struct.pack('hc', 0, __byte(0))
        #sensor3
        if opt.SENSE3_EN:
            if USE_PI_SENSE_HAT:
                sens3 = info['sens4']
                temp = sens3['Pressure_Temper']
            else:
                sens3 = info['sens3']
                temp = sens3['Temperature']
            rec += struct.pack('hhhh', __short(temp), __short(sens3['Pressure']),
                               __short(sens3['Altitude']), __short(sens3['SeaPressure']))
        else:
            rec += struct.pack('hhhh', 0, 0, 0, 0)
        #web
        rec += struct.pack('hc', __short(info['web']['Temperature']), __byte(info['web']['Humidity']))
        with open(file_path, 'ab') as f:
            f.write(rec)
    except Exception as e:
        print('Fail to save info to file:', e)

#test save_info_binary()
def test_save_info_binary():
    global info
    info = {'sens1': {'Temperature': 25.5, 'Humidity': 50}, 
            'sens2': {'Temperature': 26.5, 'Humidity': 60}, 
            'sens3': {'Temperature': 27.5, 'Pressure': 1013.2, 'Altitude': 215.3, 'SeaPressure': 1010.5}, 
            'web': {'Temperature': 28.5, 'Humidity': 70}}
    save_info_binary()


repo_info = {'day':'0', 'time':'0:0:0', 'info':{}}

#load file return as a list of repo_info
def load_info():
    try:
        #year = __get_year()
        #directory = os.path.join('repository', year)
        os.makedirs(DIR, exist_ok=True)
        file_path = os.path.join(DIR, FILE + '-' + __get_year_month())
        with open(file_path, 'r') as f:
            lines = f.readlines()
            repo_info_list = []
            for line in lines:
                line = line.strip()
                day_str, time_str, info_str = line.split(' ', 2)
                repo_info_list.append({'day': day_str, 'time': time_str, 'info': ast.literal_eval(info_str)})
            return repo_info_list
    except Exception as e:
        print('Fail to load info from file:', e)
        return []


#load binary file return as a list of repo_info
def load_info_binary(year=0, month=0, day=0, hour=-1, min=-1, backhours=24):
    #estimate start epoch time and back epoch time
    if (year == 0) and (month == 0):
        year_month_str  = __get_year_month()
    elif (year == 0) and (month != 0):
        year_month_str = __get_year() + '-' + str(month).zfill(2)
    elif (year != 0) and (month == 0):
        year_month_str = str(year) + '-' + __get_year_month().split('-')[1]
    else:
        year_month_str = str(year) + '-' + str(month).zfill(2)
    if day == 0:
        day = int(time.strftime('%d', time.localtime()))    
    if hour == -1:
        hour = int(time.strftime('%H', time.localtime()))
    if min == -1:
        min = int(time.strftime('%M', time.localtime()))
    year, month = int(year_month_str.split('-')[0]), int(year_month_str.split('-')[1])
    startepoch = get_epoch(year, month, day, hour, min)
    backepoch = startepoch - backhours * 3600
    #the back time can start in earlier month files (e.g. 24 h graph on the 1st)
    months = [(year, month)]
    while get_epoch(months[0][0], months[0][1], 1, 0, 0) > backepoch:
        y, m = months[0]
        months.insert(0, (y - 1, 12) if m == 1 else (y, m - 1))
    repo_info_list = []
    for y, m in months:
        __load_month_binary(y, m, backepoch, startepoch, repo_info_list)
    return repo_info_list

#append the records of one month file between backepoch and startepoch to repo_info_list
#values are returned as saved, a disabled sensor (options SENSEx_EN=0) was saved as zeros
def __load_month_binary(year, month, backepoch, startepoch, repo_info_list):
    try:
        file_path = os.path.join(DIR, FILE + '-' + str(year) + '-' + str(month).zfill(2) + '.bin')
        print('file_path:', file_path)
        if not os.path.exists(file_path):
            return
        with open(file_path, 'rb') as f:
            while True:
                rec_id = f.read(1)
                if not rec_id:
                    break
                if rec_id[0] != RECID:
                    continue
                fday = int.from_bytes(f.read(1), 'big')
                ftime = ':'.join([str(int.from_bytes(f.read(1), 'big')) for i in range(3)])
                sens1_temp, sens1_hum = struct.unpack('hc', f.read(3))
                sens2_temp, sens2_hum = struct.unpack('hc', f.read(3))
                sens3_temp, sens3_press, sens3_alt, sens3_sea = struct.unpack('hhhh', f.read(8))
                web_temp, web_hum = struct.unpack('hc', f.read(3))
                recordepoch = get_epoch(year, month, fday, int(ftime.split(':')[0]), int(ftime.split(':')[1]))
                if(recordepoch < backepoch) or (recordepoch > startepoch):
                    continue
                sens1 = {'Temperature': sens1_temp/10, 'Humidity': sens1_hum[0]}
                sens2 = {'Temperature': sens2_temp/10, 'Humidity': sens2_hum[0]}
                sens3 = {'Temperature': sens3_temp/10, 'Pressure': sens3_press/10, 'Altitude': sens3_alt/10, 'SeaPressure': sens3_sea/10}
                repo_info_list.append({'day': str(fday), 'time': ftime, 'epoch': recordepoch,
                                       'info': {'sens1': sens1, 'sens2': sens2, 'sens3': sens3,
                                                'web': {'Temperature': web_temp/10, 'Humidity': web_hum[0]}}})
    except Exception as e:
        print('Fail to load info from file:', e)

#test load_info_binary()
def test_load_info_binary():
    #get month, day, backhours from stdin
    month = int(input('Enter month:'))
    day = int(input('Enter day:'))
    backhours = int(input('Enter backhours:'))
    info_list = load_info_binary(month=month, day=day, hour=23, min=59, backhours=backhours)
    for info in info_list:
        print(info)
    
#test load_info()
if __name__ == '__main__':
    #test_save_info_binary()
    test_load_info_binary()
    #print(load_info())






    






