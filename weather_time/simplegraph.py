import tkinter as tk
import time as tm
import repository as repo

LCD_SIZE = '320x240'
FULL_SCREEN = 1

CURRENT_PLOT = 1
backhours = 48
win_col = "light yellow"

line_id=0

time_data = []
web_temper_data = []
web_humid_data = []
sens_press_data = []

web_temp_rng = [0,0]
web_humid_rng = [0,0]
sens_press_rng = [0,0]

web_temp_plt = True
web_humid_plt = False
sens_press_plt = False

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
        web_temp_rng[0] = min(web_temper_data)
        web_temp_rng[1] = max(web_temper_data)
        web_humid_rng[0] = min(web_humid_data)
        web_humid_rng[1] = max(web_humid_data)
        sens_press_rng[0] = min(sens_press_data)
        sens_press_rng[1] = max(sens_press_data)
    print('temp  min:%.1f max:%.1f' % ( web_temp_rng[0],  web_temp_rng[1]))    
    print('humid min:%.1f max:%.1f' % ( web_humid_rng[0],  web_humid_rng[1])) 
    print('press min:%.1f max:%.1f' % ( sens_press_rng[0],  sens_press_rng[1])) 

#################################################################

def btn_change():
    global line_id,canvas
    global web_temp_plt,web_humid_plt,sens_press_plt
    line_id += 1
    if line_id > 2:
        line_id = 0
    if line_id==0:
        web_temp_plt=True
        web_humid_plt=False
        sens_press_plt=False
    elif line_id==1:
        web_temp_plt=False
        web_humid_plt=True
        sens_press_plt=False   
    elif line_id==2:
        web_temp_plt=False
        web_humid_plt=False
        sens_press_plt=True              
    draw_plots(canvas)


def btn_both():
    global canvas
    global web_temp_plt,web_humid_plt,sens_press_plt    
    web_temp_plt=True
    web_humid_plt=True
    sens_press_plt=True
    draw_plots(canvas)


def btn_exit(win):
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

def draw_plots(canvas):
    #get height and width of canvas    
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    #print(width,height)    
    #draw rectangle
    canvas.create_rectangle(2,2,width-3,height-3,fill='white')
    #get limits
    min_temp = web_temp_rng[0]
    max_temp = web_temp_rng[1]
    min_humid = web_humid_rng[0]
    max_humid = web_humid_rng[1]
    min_press = sens_press_rng[0]
    max_press = sens_press_rng[1]
    max_time = len(time_data)
    print('plot start')
    #draw info data
    for i in range(max_time-1):
        x1 = find_screen_pos(0,max_time,i,5,width-5)
        x2 = find_screen_pos(0,max_time,i+1,5,width-5)
        #draw web_temper_data
        if web_temp_plt :
            y1 = find_screen_pos(min_temp,max_temp,web_temper_data[i],height-5,5)
            y2 = find_screen_pos(min_temp,max_temp,web_temper_data[i+1],height-5,5)
            canvas.create_line(x1,y1,x2,y2,fill='red')    
        #draw web_humid_data
        if web_humid_plt :
            y1 = find_screen_pos(min_humid,max_humid,web_humid_data[i],height-5,5)
            y2 = find_screen_pos(min_humid,max_humid,web_humid_data[i+1],height-5,5)
            canvas.create_line(x1,y1,x2,y2,fill='blue')
        #draw sens_press_data
        if sens_press_plt :
            y1 = find_screen_pos(min_press,max_press,sens_press_data[i],height-5,5)
            y2 = find_screen_pos(min_press,max_press,sens_press_data[i+1],height-5,5)
            canvas.create_line(x1,y1,x2,y2,fill='green')    
    print('plot end')


def on_resize(event):
    # Redraw the plots when the canvas is resized    
    draw_plots(event.widget)


def draw_form(win):
    global canvas
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
    canvfrm = tk.Frame(win, relief=tk.GROOVE,  borderwidth=2)
    canvas = tk.Canvas(canvfrm, bg='light steel blue')
    #draw_plots(canvas)
    canvas.pack(fill=tk.BOTH, expand=tk.YES)
    canvfrm.pack(side=tk.TOP, padx=0, pady=0, fill=tk.BOTH, expand=tk.YES)
    # Bind the resize event to update the canvas size
    canvas.bind("<Configure>", on_resize)
   

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