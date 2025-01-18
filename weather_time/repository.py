
import time

FILE='sensor' #file name to save info

info = {'sens1':{}, 'sens2':{}, 'sens3':{}}

#get year_moth string
def __get_year_month():
    return time.strftime('%Y-%m', time.localtime())

#save info with timestamb to file in a line
def save_info():
    try:
        with open(FILE+'-'+__get_year_month() , 'a') as f:
            f.write(time.strftime('%d %H:%M:%S', time.localtime())+' ')
            f.write(str(info)+'\n')
    except: 
        print('Fail to save info to file')




