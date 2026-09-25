
import time as tm
import threading as thrd
import weather as wthr
import aht10sense as sense1
import si7021sense as sense2
import mpl3115sense as sense3
import pihatsense as sense4
import repository as repo
import simplegraph as plot

USE_PI_SENSE_HAT = 1 #TODO: must auto detect

exit = False
wthr_count = 0
wthr_pressure = 1013  #for set MPL3115 sea pressure


#======== Weather Thread ======
def weather_thread(tmout):
     global exit,wthr_count,wthr_pressure
     tm_cnt=0
     wthr_count=1
     try:
        info = wthr.get_weather_info()
        wthr_pressure = info['Pressure']         
     except Exception:
        pass         
     while True:          
          if exit:
               break
          tm_cnt += 1
          if tm_cnt>tmout:
            wthr_count += 1
            try:
                info = wthr.get_weather_info()
                wthr_pressure = info['Pressure']
                if exit:
                   break            
            except Exception:
                pass            
            tm_cnt=0
          tm.sleep(1)

#======== Sensor Thread ======

def update_seaPressure(info):
    global wthr_pressure
    seaPress = info['SeaPressure']
    if seaPress != wthr_pressure:
        if USE_PI_SENSE_HAT:
            sense4.set_sea_pressure(wthr_pressure)
        else:    
            sense3.set_sea_pressure(wthr_pressure)
        print('Update mpl1315 sea pressure : %d' %wthr_pressure)


def read_sensors_info():
    print('*read_sensors_info*')
    repo.info['sens1'] = sense1.get_sensor_info()
    repo.info['sens2'] = sense2.get_sensor_info()    
    repo.info['sens3'] = sense3.get_sensor_info()        
    repo.info['sens4'] = sense4.get_sensor_info()
    if USE_PI_SENSE_HAT:
        update_seaPressure(repo.info['sens4'])
    else:
        update_seaPressure(repo.info['sens3'])
    repo.info['web'] = wthr.get_small_info()
    repo.save_info_binary()
    debug_print()


def get_sensors_info(sense_id):
    if sense_id==1:
        if USE_PI_SENSE_HAT:
            return repo.info['sens4']
        else:
            return repo.info['sens1']
    elif sense_id==2:
        return repo.info['sens2']
    elif sense_id==3:
        if USE_PI_SENSE_HAT:
            return repo.info['sens4']
        else:
            return repo.info['sens3']
    else:
        return repo.info['sens1']


def debug_print():
    print("")
    try:
        print("Web Temper=%s" % repo.info['web']['Temperature'])
        print("Web Humidity=%s" % repo.info['web']['Humidity'])
        print('S1 Temperature=%s' % repo.info['sens1']['Temperature'])
        print('S1 Humidity=%s' % repo.info['sens1']['Humidity'])
    except Exception:
        pass


def sensor_thread(tmout):
    global exit
    sense_tm_cnt=0
    try:
        read_sensors_info()
    except Exception:
        pass    
    while True:          
        if exit:
            break
        sense_tm_cnt += 1        
        if sense_tm_cnt>tmout:
            try:
                read_sensors_info()
                if exit:
                   break             
            except Exception:
                pass
            sense_tm_cnt=0

        tm.sleep(1)


def stop_threads():
    global exit
    exit = True

def run_graph():
    print("Running graph...")
    plot.main()

if __name__ == '__main__':
    # start wheather thread
    wether_thrd=thrd.Thread(target=weather_thread, args=(120,), daemon=True) # sec update
    wether_thrd.start()
    # start sensor thread
    sensor_thrd=thrd.Thread(target=sensor_thread, args=(60,), daemon=True) # sec update
    sensor_thrd.start()    
    print("Sensors server is running")

    #menu for exit or run_graph
    while True:
        cmd = input("Enter command (exit/graph): ").strip().lower()
        if cmd == "exit":
            stop_threads()
            break
        elif cmd == "graph":
            run_graph()

    wether_thrd.join(timeout=1)
    sensor_thrd.join(timeout=1)
    print("End...")