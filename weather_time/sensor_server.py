## sensor_server: poll weather site and sensors, update repository
## runs as a daemon (see sensor_server.service), raspi_play only displays and does not save

import time as tm
import threading as thrd
import signal
import argparse
import weather as wthr
import aht10sense as sense1
import si7021sense as sense2
import mpl3115sense as sense3
import pihatsense as sense4
import repository as repo

SENSOR_PERIOD  = 60   # sec, read sensors and save a record
WEATHER_PERIOD = 120  # sec, poll weather site

USE_PI_SENSE_HAT = repo.USE_PI_SENSE_HAT

stop_event = thrd.Event()

wthr_pressure = 1013   # for set sea pressure (altitude), last good web value


def log(msg):
    print(tm.strftime('%Y-%m-%d %H:%M:%S ') + msg, flush=True)


#======== Weather ========
def poll_weather():
    global wthr_pressure
    try:
        info = wthr.get_weather_info()
    except Exception as e:
        info = {'Error': str(e)}
    if info['Error'] != '':
        log('weather error: ' + info['Error'])
        return
    press = info['Pressure']
    # a failed request leaves Pressure at 0, never use it as sea pressure
    if isinstance(press, (int, float)) and press > 0:
        wthr_pressure = press


#======== Sensors ========
def update_seaPressure(info):
    if info['SeaPressure'] != wthr_pressure:
        if USE_PI_SENSE_HAT:
            sense4.set_sea_pressure(wthr_pressure)
        else:
            sense3.set_sea_pressure(wthr_pressure)
        log('update sea pressure : %d' % wthr_pressure)


def read_sensors():
    repo.info['sens1'] = dict(sense1.get_sensor_info())
    repo.info['sens2'] = dict(sense2.get_sensor_info())
    repo.info['sens3'] = dict(sense3.get_sensor_info())
    repo.info['sens4'] = dict(sense4.get_sensor_info())
    if USE_PI_SENSE_HAT:
        update_seaPressure(repo.info['sens4'])
    else:
        update_seaPressure(repo.info['sens3'])
    repo.info['web'] = dict(wthr.get_small_info())


#======== Main loop ========
def run(sensor_period, weather_period, once=False):
    next_weather = 0
    next_sensor = 0
    while not stop_event.is_set():
        now = tm.time()
        if now >= next_weather:
            poll_weather()
            next_weather = now + weather_period
        if now >= next_sensor:
            try:
                read_sensors()
                repo.save_info_binary()
            except Exception as e:
                log('sensor error: %s' % e)
            next_sensor = now + sensor_period
        if once:
            break
        stop_event.wait(max(0, min(next_weather, next_sensor) - tm.time()))


def stop(signum, frame):
    log('stop signal %d' % signum)
    stop_event.set()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='poll weather and sensors, update repository')
    parser.add_argument('--sensor-period', type=int, default=SENSOR_PERIOD, help='sec between sensor records')
    parser.add_argument('--weather-period', type=int, default=WEATHER_PERIOD, help='sec between weather polls')
    parser.add_argument('--once', action='store_true', help='poll once and exit')
    args = parser.parse_args()
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    log('sensor_server start, repository: ' + repo.DIR)
    run(args.sensor_period, args.weather_period, args.once)
    log('sensor_server end')
