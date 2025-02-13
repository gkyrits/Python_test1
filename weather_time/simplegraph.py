import tkinter as tk
import time as tm
import repository as repo

LCD_SIZE = '320x240'
FULL_SCREEN = 1

CURRENT_PLOT = 1
backhours = 48
win_col = "light yellow"
canvas_col = "snow2"
win_font=('Arial', 7)
win_fontB=('Arial', 7, 'bold')
but_font=('Arial', 8, 'bold')

canvas_inf_space = 14

time_data = []
web_temp_data = []
web_humid_data = []
sens_press_data = []
sens_temp_data = []
sens_humid_data = []

web_temp_rng = [0,0]
web_humid_rng = [0,0]
sens_press_rng = [0,0]
sens_temp_rng = [0,0]
sens_humid_rng = [0,0]

web_temp_col = 'red'
web_humid_col = 'blue'
sens_press_col = 'green'
sens_temp_col = 'magenta'
sens_humid_col = 'steel blue'

web_temp_val   = True
web_humid_val  = False
sens_press_val = False
sens_temp_val  = False
sens_humid_val = False 

pltpadx=3
replot_needed = False
backhours_changed = False
backepoch = 0

infofrm = None
backhours_lbl = None

############################################################

def clear_data():
    global time_data,web_temp_data,web_humid_data
    time_data.clear()    
    web_temp_data.clear()
    web_humid_data.clear()
    sens_press_data.clear()
    sens_temp_data.clear()
    sens_humid_data.clear()


def parce_info(year,month,backepoch,info):
    recordepoch = repo.get_epoch(year, month, int(info['day']), int(info['time'].split(':')[0]), int(info['time'].split(':')[1]))
    sens1 = info['info']['sens1']
    sens2 = info['info']['sens2']
    sens3 = info['info']['sens3']
    web = info['info']['web']
    rec_time = (recordepoch - backepoch)/60 #in minutes    
    rec_web_temp = web['Temperature']
    rec_web_humid = web['Humidity']
    rec_sens_press = sens3['Pressure']
    rec_sens_temp = sens1['Temperature']
    rec_sens_humid = sens1['Humidity']
    #check if data is in range
    if rec_web_temp < -20 or rec_web_temp > 50:
        return
    if rec_web_humid < 0 or rec_web_humid > 100:
        return
    if rec_sens_press < 900 or rec_sens_press > 1100:
        return
    #check if data is not more diff from previous data
    if len(time_data) > 0:
        last_web_temp = web_temp_data[-1]
        if abs(last_web_temp - rec_web_temp) > 10:
            rec_web_temp = last_web_temp
            #return
        last_web_humid = web_humid_data[-1]
        if abs(last_web_humid - rec_web_humid) > 10:
            rec_web_humid = last_web_humid
            #return
        last_web_press = sens_press_data[-1]
        if abs(last_web_press - rec_sens_press) > 5:
            rec_sens_press = last_web_press
            #return
        if abs(sens_temp_data[-1] - rec_sens_temp) > 5:
            rec_sens_temp = sens_temp_data[-1]
            #return
        if abs(sens_humid_data[-1] - rec_sens_humid) > 5:
            rec_sens_humid = sens_humid_data[-1]
            #return    
    #add data to lists
    time_data.append(rec_time)
    web_temp_data.append(rec_web_temp)
    web_humid_data.append(rec_web_humid)
    sens_press_data.append(rec_sens_press)
    sens_temp_data.append(rec_sens_temp)
    sens_humid_data.append(rec_sens_humid)


def get_initdata():
    global backepoch
    print('---read data file---')
    year = tm.localtime().tm_year
    if CURRENT_PLOT==1:
        month = tm.localtime().tm_mon
        day = tm.localtime().tm_mday
        hour = tm.localtime().tm_hour
        mint = tm.localtime().tm_min
    else:
        month = 1
        day=31
        hour=23
        mint=59
    startepoch = repo.get_epoch(year, month, day, hour, mint)
    backepoch = startepoch - backhours * 3600
    info_list = repo.load_info_binary(year, month, day, hour, mint, backhours)
    clear_data()
    if info_list:
        for info in info_list:
            parce_info(year,month,backepoch,info)
    if len(time_data)>0 :
        web_temp_rng[0] = min(web_temp_data)
        web_temp_rng[1] = max(web_temp_data)
        web_humid_rng[0] = min(web_humid_data)
        web_humid_rng[1] = max(web_humid_data)
        sens_press_rng[0] = min(sens_press_data)
        sens_press_rng[1] = max(sens_press_data)
        sens_temp_rng[0] = min(sens_temp_data)
        sens_temp_rng[1] = max(sens_temp_data)
        sens_humid_rng[0] = min(sens_humid_data)
        sens_humid_rng[1] = max(sens_humid_data)
    print('w  temp  min:%.1f max:%.1f' % ( web_temp_rng[0],  web_temp_rng[1]))    
    print('s1 temp  min:%.1f max:%.1f' % ( sens_temp_rng[0],  sens_temp_rng[1]))
    print('w  humid min:%.1f max:%.1f' % ( web_humid_rng[0],  web_humid_rng[1])) 
    print('s1 humid min:%.1f max:%.1f' % ( sens_humid_rng[0],  sens_humid_rng[1]))
    print('s3 press min:%.1f max:%.1f' % ( sens_press_rng[0],  sens_press_rng[1]))

#################################################################

def plotCbx_change():
    global replot_needed
    replot_needed = True    


def btn_exit(win):
    global web_temp_val,web_humid_val,sens_press_val,sens_temp_val,sens_humid_val
    web_temp_val = web_temp_var.get()
    web_humid_val = web_humid_var.get()
    sens_press_val = sens_press_var.get()
    sens_temp_val = sens_temp_var.get()
    sens_humid_val = sens_humid_var.get()    
    win.destroy() 


def find_screen_pos(min_val, max_val, val, min_pos, max_pos):
    val_mxmn = max_val - min_val
    pos_mxmn = max_pos - min_pos
    k = pos_mxmn / val_mxmn
    d1 = val - min_val
    fd2 = d1 * k
    fvalue = min_pos + fd2
    value = round(fvalue)
    return value


def draw_plot_time_info(canvas):
    global backepoch
    ypos=8; xpos=5
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    #draw time info
    if len(time_data)>0 :
        starttime=tm.strftime('%d/%H:%M',tm.localtime(backepoch+time_data[0]*60))
        endtime=tm.strftime('%d/%H:%M',tm.localtime(backepoch+time_data[-1]*60))
        canvas.create_text(xpos,height-ypos,text=starttime, font=win_font, anchor=tk.W)
        canvas.create_text(width-xpos,height-ypos,text=endtime, font=win_font, anchor=tk.E)


def draw_limits():
    global leftfrm,infofrm
    if infofrm:
        infofrm.destroy()
    infofrm = tk.Frame(leftfrm, bg=win_col)
    rowidx=0
    if web_temp_var.get() :
        tk.Label(infofrm, text='W Temp:', fg='white', bg=web_temp_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1
        tk.Label(infofrm, text='↑ %.1f' % web_temp_rng[1], bg=win_col, fg=web_temp_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1        
        tk.Label(infofrm, text='↓ %.1f' % web_temp_rng[0], bg=win_col, fg=web_temp_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1
    if sens_temp_var.get() :
        tk.Label(infofrm, text='S Temp:', fg='white', bg=sens_temp_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1
        tk.Label(infofrm, text='↑ %.1f' % sens_temp_rng[1], bg=win_col, fg=sens_temp_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1           
        tk.Label(infofrm, text='↓ %.1f' % sens_temp_rng[0], bg=win_col, fg=sens_temp_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1
    if web_humid_var.get() :
        tk.Label(infofrm, text='W Humid:', fg='white', bg=web_humid_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1
        tk.Label(infofrm, text='↑ %.1f' % web_humid_rng[1], bg=win_col, fg=web_humid_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1        
        tk.Label(infofrm, text='↓ %.1f' % web_humid_rng[0], bg=win_col, fg=web_humid_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1
    if sens_humid_var.get() :
        tk.Label(infofrm, text='S Humid:', fg='white', bg=sens_humid_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1
        tk.Label(infofrm, text='↑ %.1f' % sens_humid_rng[1], bg=win_col, fg=sens_humid_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1        
        tk.Label(infofrm, text='↓ %.1f' % sens_humid_rng[0], bg=win_col, fg=sens_humid_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1
    if sens_press_var.get() :
        tk.Label(infofrm, text='S Press:', fg='white', bg=sens_press_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1
        tk.Label(infofrm, text='↑ %.1f' % sens_press_rng[1], bg=win_col, fg=sens_press_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1         
        tk.Label(infofrm, text='↓ %.1f' % sens_press_rng[0], bg=win_col, fg=sens_press_col, font=win_fontB).grid(row=rowidx, sticky=tk.W); rowidx += 1       
    for row in range(rowidx): 
        infofrm.rowconfigure(row, weight=1) #resize grid height         
    infofrm.pack(side=tk.TOP, fill=tk.Y)    


def draw_plots(canvas):
    #get height and width of canvas    
    width = canvas.winfo_width()
    height = canvas.winfo_height()-canvas_inf_space
    #print(width,height)    
    #draw rectangle
    canvas.delete('all')
    canvas.create_rectangle(2,2,width-3,height-3,fill=canvas_col)
    #estimate temper limits
    print('---estimate limits---')
    if web_temp_var.get() and sens_temp_var.get():
        min_temp = min(web_temp_rng[0],sens_temp_rng[0])
        max_temp = max(web_temp_rng[1],sens_temp_rng[1])     
    elif web_temp_var.get():
        min_temp = web_temp_rng[0]
        max_temp = web_temp_rng[1]        
    elif sens_temp_var.get():
        min_temp = sens_temp_rng[0]
        max_temp = sens_temp_rng[1]
    #min/max temp nearly lower 0.5 decade
    if web_temp_var.get() or sens_temp_var.get():
        print(min_temp,max_temp)       
        min_temp = min_temp - (min_temp % 5)    
        max_temp = max_temp + (5 - max_temp % 5)
        print(min_temp,max_temp)  
    #estimate humid limits
    if web_humid_var.get() and sens_humid_var.get():
        min_humid = min(web_humid_rng[0],sens_humid_rng[0])
        max_humid = max(web_humid_rng[1],sens_humid_rng[1])
    elif web_humid_var.get():
        min_humid = web_humid_rng[0]
        max_humid = web_humid_rng[1]
    elif sens_humid_var.get():
        min_humid = sens_humid_rng[0]
        max_humid = sens_humid_rng[1]            
    #min/max humid nearly lower 1 decade
    if web_humid_var.get() or sens_humid_var.get():
        print(min_humid,max_humid)
        min_humid = min_humid - (min_humid % 10)
        max_humid = max_humid + (10 - max_humid % 10)
        print(min_humid,max_humid)
    #estimate press limits
    if sens_press_var.get() :
        min_press = sens_press_rng[0]
        max_press = sens_press_rng[1]
        #min/max press nearly lower 1 decade
        print(min_press,max_press)
        min_press = min_press - (min_press % 10)
        max_press = max_press + (10 - max_press % 10)
        print(min_press,max_press)
    max_time = len(time_data)
    update_rec = max_time // 60
    print('plot %d rec start' % max_time)
    #----draw info data----    
    for i in range(max_time-1):
        x1 = find_screen_pos(0,max_time,i,pltpadx,width-pltpadx)
        x2 = find_screen_pos(0,max_time,i+1,pltpadx,width-pltpadx)
        #draw web_temp_data
        if web_temp_var.get() :
            y1 = find_screen_pos(min_temp,max_temp,web_temp_data[i],height-pltpadx,pltpadx)
            y2 = find_screen_pos(min_temp,max_temp,web_temp_data[i+1],height-pltpadx,pltpadx)
            canvas.create_line(x1,y1,x2,y2,fill=web_temp_col)    
        #draw web_humid_data
        if web_humid_var.get() :
            y1 = find_screen_pos(min_humid,max_humid,web_humid_data[i],height-pltpadx,pltpadx)
            y2 = find_screen_pos(min_humid,max_humid,web_humid_data[i+1],height-pltpadx,pltpadx)
            canvas.create_line(x1,y1,x2,y2,fill=web_humid_col)
        #draw sens_press_data
        if sens_press_var.get() :
            y1 = find_screen_pos(min_press,max_press,sens_press_data[i],height-pltpadx,pltpadx)
            y2 = find_screen_pos(min_press,max_press,sens_press_data[i+1],height-pltpadx,pltpadx)
            canvas.create_line(x1,y1,x2,y2,fill=sens_press_col)  
        #draw sens_temp_data
        if sens_temp_var.get() :
            y1 = find_screen_pos(min_temp,max_temp,sens_temp_data[i],height-pltpadx,pltpadx)
            y2 = find_screen_pos(min_temp,max_temp,sens_temp_data[i+1],height-pltpadx,pltpadx)
            canvas.create_line(x1,y1,x2,y2,fill=sens_temp_col)
        #draw sens_humid_data
        if sens_humid_var.get() :
            y1 = find_screen_pos(min_humid,max_humid,sens_humid_data[i],height-pltpadx,pltpadx)
            y2 = find_screen_pos(min_humid,max_humid,sens_humid_data[i+1],height-pltpadx,pltpadx)
            canvas.create_line(x1,y1,x2,y2,fill=sens_humid_col)
        #update canvas every some points        
        if (i % update_rec == 0) and (i > 0):
            #print('plot %d rec' % i)
            canvas.update()    
    print('plot end')
    canvas.update()
    draw_plot_time_info(canvas)
    draw_limits()


def canvas_resize(event):
    # Redraw the plots when the canvas is resized    
    draw_plots(event.widget)    


def canvas_click(event):
    global replot_needed,backhours_changed,backepoch
    print('click at:',event.x,event.y)
    if backhours_changed:
        get_initdata()
        draw_plots(canvas)
        backhours_changed = False
        return
    if replot_needed:
        draw_plots(canvas)
        replot_needed = False
        return
    if len(time_data)==0 :
        return
    #get time from x
    width = canvas.winfo_width()
    #height = canvas.winfo_height()-canvas_inf_space
    timeidx = find_screen_pos(pltpadx,width-pltpadx,event.x,0,len(time_data))
    if timeidx >= len(time_data):
        timeidx = len(time_data)-1
    if timeidx < 0:
        timeidx = 0     
    clicktime=tm.strftime('(%d/%H:%M)',tm.localtime(backepoch+time_data[timeidx]*60))
    print('timeidx:%d date:%s' % (timeidx,clicktime))
    #print clicktime to canvas    
    height = canvas.winfo_height()
    width = canvas.winfo_width()
    ypos=8; xpos=(width-len(clicktime))/2-15
    canvas.delete('clicktime')    
    canvas.create_text(xpos,height-ypos, text=clicktime, font=win_font, anchor=tk.W, tags='clicktime')
    #draw vertical line
    canvas.delete('clickline')
    canvas.create_line(event.x,0,event.x,height-13,fill='black',dash=(2,2),tags='clickline')



def backhours_change(inc):
    global backhours,backhours_changed,backhours_lbl
    if inc:
        if backhours < 6:
            backhours=6
        elif backhours < 12:
            backhours=12
        elif backhours < 24:
            backhours=24
        else:
            backhours += 24
    else:
        if backhours >= 48:
            backhours -= 24
        elif backhours >= 24:
            backhours = 12
        elif backhours >= 12:
            backhours = 6
        elif backhours >= 6:
            backhours = 3              
    backhours_changed = True     
    backhours_lbl.config(text=get_backhours_str())


def get_backhours_str():
    if backhours <= 24:
        return str(backhours)+'h'
    else:
        return str(backhours//24)+'d'    


def draw_form(win):
    global canvas,leftfrm,backhours_lbl
    global web_temp_var,web_humid_var,sens_press_var,sens_temp_var,sens_humid_var
    web_temp_var = tk.BooleanVar(value=web_temp_val)
    web_humid_var = tk.BooleanVar(value=web_humid_val)
    sens_press_var = tk.BooleanVar(value=sens_press_val)
    sens_temp_var = tk.BooleanVar(value=sens_temp_val)
    sens_humid_var = tk.BooleanVar(value=sens_humid_val)
    #get data from repository
    get_initdata()
    #set background color to toplevel win
    win.config(bg=win_col)
    #tools Frame    
    toolsfrm = tk.Frame(win, bg=win_col, height=25)
    #webFrmTools
    webFrmTools = tk.Frame(toolsfrm, relief=tk.GROOVE, borderwidth=2 , bg=win_col)
    tk.Label(webFrmTools, text='W:', font=win_font, width=2).pack(side=tk.LEFT)
    tk.Checkbutton(webFrmTools, text='T', bg='light pink', font=win_font, width=1, variable=web_temp_var, command=plotCbx_change).pack(side=tk.LEFT)
    tk.Checkbutton(webFrmTools, text='H', bg='light blue', font=win_font, width=1, variable=web_humid_var, command=plotCbx_change).pack(side=tk.LEFT)
    webFrmTools.pack(side=tk.LEFT, padx=2)
    #sensFrmTools
    sensFrmTools = tk.Frame(toolsfrm, relief=tk.GROOVE, borderwidth=2 , bg=win_col)
    tk.Label(sensFrmTools, text='S:', font=win_font, width=1).pack(side=tk.LEFT)
    tk.Checkbutton(sensFrmTools, text='T', bg='light pink', font=win_font, width=1, variable=sens_temp_var, command=plotCbx_change).pack(side=tk.LEFT)
    tk.Checkbutton(sensFrmTools, text='H', bg='light blue', font=win_font, width=1, variable=sens_humid_var, command=plotCbx_change).pack(side=tk.LEFT)
    tk.Checkbutton(sensFrmTools, text='P', bg='light green', font=win_font, width=1, variable=sens_press_var, command=plotCbx_change).pack(side=tk.LEFT)
    sensFrmTools.pack(side=tk.LEFT, padx=6)     
    #exit button
    tk.Button(toolsfrm, text='Exit', font=win_font, command=lambda:btn_exit(win)).pack(side=tk.RIGHT, padx=2)
    toolsfrm.pack(side=tk.BOTTOM, padx=2, pady=2, fill=tk.X) 
    toolsfrm.pack_propagate(False) #enable Frame height
    #top Frame
    topfrm = tk.Frame(win, bg=win_col)
    #left info Frame
    leftfrm = tk.Frame(topfrm, bg=win_col, width=50)
    #infofrm = tk.Frame(leftfrm, bg=win_col)
    #tk.Label(infofrm, text='Web:', bg='light yellow', font=win_font).pack(side=tk.TOP)
    #infofrm.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    leftfrm.pack(side=tk.LEFT, padx=2, pady=4, fill=tk.Y)
    leftfrm.pack_propagate(False) #enable Frame with
    #canvas tool Frame
    canvtoolfrm = tk.Frame(topfrm, bg=win_col, height=20)
    tk.Button(canvtoolfrm, text='<', font=but_font, width=2).pack(side=tk.LEFT, padx=0)
    tk.Button(canvtoolfrm, text='-', font=but_font, width=2, command=lambda:backhours_change(False)).pack(side=tk.LEFT, padx=2)
    backhours_lbl=tk.Label(canvtoolfrm, text=get_backhours_str(), bg=win_col, fg='red', font=but_font)
    backhours_lbl.pack(side=tk.LEFT)
    tk.Button(canvtoolfrm, text='+', font=but_font, width=2, command=lambda:backhours_change(True)).pack(side=tk.LEFT, padx=2)
    tk.Button(canvtoolfrm, text='>', font=but_font, width=2).pack(side=tk.LEFT, padx=0)
    canvtoolfrm.pack(side=tk.BOTTOM, padx=0, pady=0, fill=tk.X)
    canvtoolfrm.pack_propagate(False) #enable Frame height
    #canvas Frame
    canvfrm = tk.Frame(topfrm, relief=tk.GROOVE,  borderwidth=2)
    canvas = tk.Canvas(canvfrm, bg=canvas_col)
    #draw_plots(canvas)
    canvas.pack(fill=tk.BOTH, expand=tk.YES)
    canvfrm.pack(side=tk.TOP, padx=0, pady=0, fill=tk.BOTH, expand=tk.YES)
    # Bind the resize event to update the canvas size
    canvas.bind("<Configure>", canvas_resize)
    canvas.bind("<Button-1>",  canvas_click)
    topfrm.pack(side=tk.TOP, padx=2, pady=2, fill=tk.BOTH, expand=tk.YES)
   

#################################################################

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Test Graph')
    root.geometry(LCD_SIZE+'+0+0')
    if FULL_SCREEN:
        root.overrideredirect(1)    
    root.config(bg=win_col)
    draw_form(root)
    root.mainloop()
    print('End of program')