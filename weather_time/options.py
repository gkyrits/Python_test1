import tkinter as tk
import os
import sys
import json


LCD_SIZE = '320x240'
FULL_SCREEN = 0 if sys.platform.startswith('win') else 1  # normal window for testing on Windows

EN=0
GR=1
LANG=GR

locations = {
    1: {"name": "Nea Smyrni", "lat": 37.93820, "lon": 23.70925}
}

# enable(1)/disable(0) room sensors: not read, not shown, not saved/read in repository
SENSE1_EN = 1   # sensor 1: Sense HAT or AHT10 temperature/humidity
SENSE2_EN = 1   # sensor 2: SI7021 temperature/humidity
SENSE3_EN = 1   # sensor 3: Sense HAT or MPL3115 pressure/altitude

# sensor calibration offsets, added to every reading (web values have none)
AHT10_TEMP_OFFSET  = 0.0   # °C
AHT10_HUMID_OFFSET = 0.0   # %
SI7021_TEMP_OFFSET  = 0.0  # °C
SI7021_HUMID_OFFSET = 0.0  # %
MPL3115_TEMP_OFFSET  = 0.0   # °C
MPL3115_PRESS_OFFSET = 0.0   # hPa
MPL3115_ALTIT_OFFSET = 0.0   # m
SENSEHAT_TEMP_OFFSET       = 0.0  # °C (humidity sensor temperature)
SENSEHAT_HUMID_OFFSET      = 0.0  # %
SENSEHAT_PRESS_TEMP_OFFSET = 0.0  # °C (pressure sensor temperature)
SENSEHAT_PRESS_OFFSET      = 0.0  # hPa, altitude is calculated from the corrected pressure

# values above are defaults, the ones edited in the options form are saved in
# options.json (next to this file) and loaded on start
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'options.json')
SAVED_NAMES = ('SENSE1_EN', 'SENSE2_EN', 'SENSE3_EN',
               'AHT10_TEMP_OFFSET', 'AHT10_HUMID_OFFSET',
               'SI7021_TEMP_OFFSET', 'SI7021_HUMID_OFFSET',
               'MPL3115_TEMP_OFFSET', 'MPL3115_PRESS_OFFSET', 'MPL3115_ALTIT_OFFSET',
               'SENSEHAT_TEMP_OFFSET', 'SENSEHAT_HUMID_OFFSET',
               'SENSEHAT_PRESS_TEMP_OFFSET', 'SENSEHAT_PRESS_OFFSET')
settings_mtime = 0  # modification time of the loaded settings file


def save():
    global settings_mtime
    data = {name: globals()[name] for name in SAVED_NAMES}
    tmp_file = SETTINGS_FILE + '.tmp'
    try:
        with open(tmp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_file, SETTINGS_FILE)  # never leave a half written file
        settings_mtime = os.path.getmtime(SETTINGS_FILE)  # no reload of our own save
    except Exception as e:
        print('Fail to save options:', e)


def load():
    global settings_mtime
    try:
        settings_mtime = os.path.getmtime(SETTINGS_FILE)
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return  # no saved settings, keep defaults
    except Exception as e:
        print('Fail to load options:', e)
        return
    for name in SAVED_NAMES:
        if name in data:
            try:
                globals()[name] = type(globals()[name])(data[name])  # keep int/float type
            except (TypeError, ValueError):
                print('Bad option value %s: %s' % (name, data[name]))


# load again if the file changed (saved by an other program, or edited by hand)
def reload_if_changed():
    try:
        mtime = os.path.getmtime(SETTINGS_FILE)
    except OSError:
        return
    if mtime != settings_mtime:
        load()

# LCD size window without frame (when FULL_SCREEN)
def full_screen(win):
    if FULL_SCREEN:
        win.overrideredirect(1)


# a frameless (overrideredirect) window gets no key events from the window
# manager on Linux (Pi), so grab the keyboard while a form that needs keys is
# open; the grab ends when the window is closed
def grab_keyboard(win):
    if not (FULL_SCREEN and sys.platform.startswith('linux')):
        return
    def grab(tries):
        try:
            win.grab_set_global()
        except tk.TclError as e:
            if tries > 0 and win.winfo_exists():
                win.after(100, grab, tries-1)  # not viewable yet, try again
            else:
                print('Fail grab keyboard:', e)
    win.after(100, grab, 20)


def center_form(win, width, height):
    display_width, display_height = map(int, LCD_SIZE.split('x', 1))
    x_pos = (display_width - width) // 2
    y_pos = (display_height - height) // 2
    win.geometry(f'{width}x{height}+{x_pos}+{y_pos}')


def wait_msg(info):        
    waitWin=tk.Toplevel(bg="green")
    center_form(waitWin, 220, 80)
    waitWin.overrideredirect(1)
    bg_col="yellow green"
    frm=tk.Frame(waitWin, bg=bg_col, relief=tk.GROOVE, borderwidth=2)
    tk.Label(frm,text=info, bg=bg_col, font='bold').pack(side=tk.TOP)
    frm.pack(padx=5, pady=5, fill=tk.BOTH, expand=tk.YES)
    waitWin.lift()
    waitWin.update() #force paint now, update_idletasks() alone won't draw it on Windows
    return waitWin


load()


