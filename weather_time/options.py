import tkinter as tk


LCD_SIZE = '320x240'
FULL_SCREEN = 1

EN=0
GR=1
LANG=GR

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


