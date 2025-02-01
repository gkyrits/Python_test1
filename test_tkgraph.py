import tkinter as tk
import time as tm
import threading as thrd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

LCD_SIZE = '320x240'
FULL_SCREEN = 0


x = np.arange(0, 3 * np.pi, 0.1)
y = np.sin(x)
x1 = 1,2,3,4,5,6,7,8,9,10
y1 = 5,8,3,5,9,2,5,1,6,7
y3 = np.sin(1.5 * np.pi * x)
dflt_line=True
axes = [None,None,None]


def btn_change():
    global dflt_line
    for ax in axes:
        ax.clear()   
    axes[0].margins(0.01)
    if dflt_line:        
        axes[0].plot(x, y, label='line1', color='r')    
        dflt_line = False
    else:
        axes[0].plot(x1, y1, label='line2', color='b')        
        dflt_line = True        
    for ax in axes:
        ax.set_yticks([]) # Hide y-axis ticks
    axes[0].legend()
    axes[0].figure.canvas.draw()  


def btn_both():
    for ax in axes:
        ax.clear()
        ax.margins(0.01)
    axes[0].plot(x, y, label='line1', color='r')    
    axes[1].plot(x1, y1, label='line2', color='b')
    axes[2].plot(x, y3, label='line3', color='g')
    for ax in axes:
        ax.set_yticks([]) # Hide y-axis ticks
        ax.set_xticks([0, 2, 4, 6, 8, 10])  # Set fixed x-ticks
        #ax.set_xticks([])
        #ax.legend() 
        ax.figure.canvas.draw() 

def btn_exit():
    root.destroy()    


def get_matplot_canvas(canvfrm):    
    plt.rcParams.update({'font.size': 6})
    fig = plt.Figure()
    #fig = plt.Figure(tight_layout=False)
    axes[0] = fig.add_subplot()
    axes[1] = axes[0].twinx()
    axes[2] = axes[0].twinx()
    for ax in axes:        
        #ax.margins(0.01)
        ax.set_yticks([]) # Hide y-axis ticks
        ax.set_xticks([0, 2, 4, 6, 8, 10])  # Set fixed x-ticks
    fig.subplots_adjust(left=0, right=0.99, top=0.99, bottom=0.1)
    FigCanvas = FigureCanvasTkAgg(fig, master=canvfrm)
    FigCanvas.draw()
    return FigCanvas.get_tk_widget()


def draw_form():
    #tools
    toolsfrm = tk.Frame(root, bg=win_col, height=25)
    tk.Button(toolsfrm, text='Change', command=btn_change).pack(side=tk.LEFT, padx=4)
    tk.Button(toolsfrm, text='Both', command=btn_both).pack(side=tk.LEFT, padx=4)
    tk.Button(toolsfrm, text='Exit', command=btn_exit).pack(side=tk.LEFT, padx=4)
    toolsfrm.pack(side=tk.BOTTOM, padx=2, pady=2, fill=tk.X) 
    toolsfrm.pack_propagate(False) #enable Frame height
    #canvas
    canvfrm = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
    #canvas = tk.Canvas(canvfrm, bg='light steel blue')
    canvas = get_matplot_canvas(canvfrm)
    canvas.pack(fill=tk.BOTH, expand=tk.YES)
    canvfrm.pack(side=tk.TOP, padx=0, pady=0, fill=tk.BOTH, expand=tk.YES)
   

win_col = "light yellow"
root = tk.Tk()
root.title('Test Graph')
root.geometry(LCD_SIZE+'+0+0')
if FULL_SCREEN:
    root.overrideredirect(1)    
root.config(bg=win_col)
draw_form()

root.mainloop()