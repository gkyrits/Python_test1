import time

FILE = 'sensor'  # file name to save info

info = {'sens1': {}, 'sens2': {}, 'sens3': {}}

# get year_month string
def __get_year_month():
    return time.strftime('%Y-%m', time.localtime())

# format floats in the dictionary to 1 decimal point
def format_floats(data):
    if isinstance(data, dict):
        return {k: format_floats(v) for k, v in data.items()}
    elif isinstance(data, float):
        return f"{data:.1f}"
    elif isinstance(data, list):
        return [format_floats(i) for i in data]
    else:
        return data

# save info with timestamp to file in a line
def save_info():
    try:
        formatted_info = format_floats(info)
        with open(FILE + '-' + __get_year_month(), 'a') as f:
            f.write(time.strftime('%d %H:%M:%S', time.localtime()) + ' ')
            f.write(str(formatted_info) + '\n')
    except Exception as e:
        print('Fail to save info to file:', e)




