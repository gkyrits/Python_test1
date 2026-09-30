import tkinter as tk


LCD_SIZE = '320x240'
FULL_SCREEN = 1

EN=0
GR=1
LANG=GR

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


