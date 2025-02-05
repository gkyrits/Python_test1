import tkinter as tk
import time as tm
#import threading as thrd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#import numpy as np
import repository as repo

LCD_SIZE = '320x240'
FULL_SCREEN = 1
LINE_WIDTH = 0.5

CURRENT_PLOT = 1
backhours = 48
win_col = "light yellow"

line_id=0
axes = [None,None,None]

time_data = []
web_temper_data = []
web_humid_data = []
sens_press_data = []

############################################################

def clear_data():
    global time_data,web_temper_data,web_humid_data
    time_data.clear()    
    web_temper_data.clear()
    web_humid_data.clear()
    sens_press_data.clear()



def parce_info(year,month,backepoch,info):
    recordepoch = repo.get_epoch(year, month, int(info['day']), int(info['time'].split(':')[0]), int(info['time'].split(':')[1]))
    sens1 = info['info']['sens1']
    sens2 = info['info']['sens2']
    sens3 = info['info']['sens3']
    web = info['info']['web']
    rec_time = (recordepoch - backepoch)/60 #in minutes    
    rec_web_temp = web['Temperature']
    rec_web_humid = web['Humidity']
    rec_web_press = sens3['Pressure']
    #check if data is in range
    if rec_web_temp < -20 or rec_web_temp > 50:
        return
    if rec_web_humid < 0 or rec_web_humid > 100:
        return
    if rec_web_press < 900 or rec_web_press > 1100:
        return
    #check if data is not more diff from previous data
    if len(time_data) > 0:
        last_web_temp = web_temper_data[-1]
        if abs(last_web_temp - rec_web_temp) > 10:
            return
        last_web_humid = web_humid_data[-1]
        if abs(last_web_humid - rec_web_humid) > 10:
            return
        last_web_press = sens_press_data[-1]
        if abs(last_web_press - rec_web_press) > 5:
            return
    #add data to lists
    time_data.append(rec_time)
    web_temper_data.append(rec_web_temp)
    web_humid_data.append(rec_web_humid)
    sens_press_data.append(rec_web_press)


def get_initdata():
    year = tm.localtime().tm_year
    if CURRENT_PLOT==1:
        month = tm.localtime().tm_mon
        day = tm.localtime().tm_mday
        hour = tm.localtime().tm_hour
        min = tm.localtime().tm_min
    else:
        month = 1
        day=31
        hour=23
        min=59
    startepoch = repo.get_epoch(year, month, day, hour, min)
    backepoch = startepoch - backhours * 3600
    info_list = repo.load_info_binary(year, month, day, hour, min, backhours)
    clear_data()
    if info_list:
        for info in info_list:
            parce_info(year,month,backepoch,info)


###############################################

def btn_change():
    global line_id
    for ax in axes:
        ax.clear()   
    axes[0].margins(0.01)
    if line_id==0:                
        axes[0].plot(time_data, web_temper_data, label='web temper', color='r', linewidth=LINE_WIDTH)
        line_id = 1
    elif line_id==1:
        axes[0].plot(time_data, web_humid_data, label='web humid', color='b', linewidth=LINE_WIDTH)
        line_id = 2
    elif line_id==2:
        axes[0].plot(time_data, sens_press_data, label='pressuse', color='g', linewidth=LINE_WIDTH)
        line_id = 0
    for ax in axes:
        ax.set_yticks([]) # Hide y-axis ticks
    axes[0].legend()
    axes[0].figure.canvas.draw()  


def btn_both():
    for ax in axes:
        ax.clear()
        ax.margins(0.01)
    axes[0].plot(time_data, web_temper_data, label='web temper', color='r', linewidth=LINE_WIDTH)    
    axes[1].plot(time_data, web_humid_data, label='web humid', color='b', linewidth=LINE_WIDTH)
    axes[2].plot(time_data, sens_press_data, label='pressuse', color='g', linewidth=LINE_WIDTH)
    for ax in axes:
        ax.set_yticks([]) # Hide y-axis ticks
        #ax.set_xticks([])
        ax.legend() 
        ax.figure.canvas.draw() 

def btn_exit(win):
    win.destroy()    


def get_matplot_canvas(canvfrm):    
    plt.rcParams.update({'font.size': 6})
    fig = plt.Figure(figsize=(0.1, 0.1), dpi=100) #px, py = w*dpi, h*dpi  # pixels
    #fig = plt.Figure(tight_layout=False)
    axes[0] = fig.add_subplot()
    axes[1] = axes[0].twinx()
    axes[2] = axes[0].twinx()
    if web_temper_data :
        global line_id
        axes[0].plot(time_data, web_temper_data, label='web temper', color='r', linewidth=LINE_WIDTH)        
        line_id = 1
    for ax in axes:     
        ax.margins(0.01)           
        ax.set_yticks([]) # Hide y-axis ticks
    fig.subplots_adjust(left=0, right=0.99, top=0.99, bottom=0.1)
    FigCanvas = FigureCanvasTkAgg(fig, master=canvfrm)
    FigCanvas.draw()
    return FigCanvas.get_tk_widget()


def draw_form(win):
    #get data from repository
    get_initdata()
    #tools
    toolsfrm = tk.Frame(win, bg=win_col, height=25)
    tk.Button(toolsfrm, text='Next', command=btn_change).pack(side=tk.LEFT, padx=4)
    tk.Button(toolsfrm, text='All', command=btn_both).pack(side=tk.LEFT, padx=4)
    tk.Button(toolsfrm, text='Exit', command=lambda:btn_exit(win)).pack(side=tk.LEFT, padx=4)
    toolsfrm.pack(side=tk.BOTTOM, padx=2, pady=2, fill=tk.X) 
    toolsfrm.pack_propagate(False) #enable Frame height
    #canvas
    canvfrm = tk.Frame(win, relief=tk.GROOVE, borderwidth=2)
    #canvas = tk.Canvas(canvfrm, bg='light steel blue')
    canvas = get_matplot_canvas(canvfrm)
    canvas.pack(fill=tk.BOTH, expand=tk.YES)
    canvfrm.pack(side=tk.TOP, padx=0, pady=0, fill=tk.BOTH, expand=tk.YES)
   

##################################################

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Test Graph')
    root.geometry(LCD_SIZE+'+0+0')
    if FULL_SCREEN:
        root.overrideredirect(1)    
    root.config(bg=win_col)
    draw_form(root)
    root.mainloop()