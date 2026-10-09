## sensor_server: poll weather site and sensors, update repository
## runs as a daemon (see sensor_server.service), raspi_play only displays and does not save
## run from a terminal it also shows a menu: 1.exit 2.graph

import time as tm
import threading as thrd
import signal
import argparse
import sys
import weather as wthr
import aht10sense as sense1
import si7021sense as sense2
import mpl3115sense as sense3
import pihatsense as sense4
import repository as repo
import options as opt

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
    log('web temper: {:.1f} C, humid: {} %'.format(info['Temper'], info['Humidity']))
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


# read only the enabled sensors (options SENSEx_EN)
# sensor 1 = Sense HAT or AHT10, sensor 2 = SI7021, sensor 3 = Sense HAT or MPL3115
def read_sensors():
    opt.reload_if_changed()  # options form may have saved new settings
    if USE_PI_SENSE_HAT:
        if opt.SENSE1_EN or opt.SENSE3_EN:
            repo.info['sens4'] = dict(sense4.get_sensor_info())
    else:
        if opt.SENSE1_EN:
            repo.info['sens1'] = dict(sense1.get_sensor_info())
        if opt.SENSE3_EN:
            repo.info['sens3'] = dict(sense3.get_sensor_info())
    if opt.SENSE2_EN:
        repo.info['sens2'] = dict(sense2.get_sensor_info())
    if opt.SENSE3_EN:
        update_seaPressure(repo.info['sens4'] if USE_PI_SENSE_HAT else repo.info['sens3'])
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


#======== CLI ========
def show_graph():
    import tkinter as tk
    import simplegraph as plot
    try:
        root = tk.Tk()
    except tk.TclError as e:
        print('cannot open graph window (no display?): %s' % e)
        return
    root.title('Sensor graph')
    root.geometry(plot.LCD_SIZE + '+0+0')
    plot.draw_form(root)
    root.mainloop()


def cli():
    while not stop_event.is_set():
        print('\n1. exit\n2. graph')
        try:
            choice = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            choice = '1'
        if choice == '1':
            stop_event.set()
        elif choice == '2':
            show_graph()
        elif choice:
            print('unknown option: ' + choice)


def stop(signum, frame):
    log('stop signal %d' % signum)
    stop_event.set()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='poll weather and sensors, update repository')
    parser.add_argument('--sensor-period', type=int, default=SENSOR_PERIOD, help='sec between sensor records')
    parser.add_argument('--weather-period', type=int, default=WEATHER_PERIOD, help='sec between weather polls')
    parser.add_argument('--once', action='store_true', help='poll once and exit')
    parser.add_argument('--no-cli', action='store_true', help='no menu, run as daemon')
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, stop)
    log('sensor_server start, repository: ' + repo.DIR)
    if args.once:
        run(args.sensor_period, args.weather_period, once=True)
    else:
        poll_thrd = thrd.Thread(target=run, args=(args.sensor_period, args.weather_period))
        poll_thrd.start()
        if not args.no_cli and sys.stdin.isatty():
            cli()  # Ctrl+C or EOF also exit
        else:
            signal.signal(signal.SIGINT, stop)
            while not stop_event.wait(1):
                pass
        stop_event.set()
        poll_thrd.join()
    log('sensor_server end')
