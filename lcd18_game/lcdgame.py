import tkinter as tk
import time as tm
import threading as thrd
import lcdpager as pager
import lcdmenu as menu
import PIL.ImageTk as ImageTk
import board as brd
import sensehat as hat
#include libdir
import sys
import os
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
import ipaddr as ip
import weather as wthr
import si7021sense as sens_in

WINDOWS=True

exit=False
pause=False
on_menu=False
ip_addr="--.--.--.--"
temper="--"
humid="--"
press="--"

LCD_PLAY=1
GUI_PLAY=2
DUAL_PLAY=3
play_mode=LCD_PLAY

SENS_IN =1
SENS_WEB=2
SENS_HAT=3
sensor_id=SENS_IN
sens_dscr="IN"

gui=None
backlight_val=50

if WINDOWS:
    play_mode=GUI_PLAY

#======== Gui Class =========
class SimulateGui:
    win_col = "pink"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LDC 1.8 (160x128)")
        self.root.config(bg=self.win_col)
        if WINDOWS:
            self.root.attributes('-toolwindow', True) #windows
        self.root.resizable(0,0)
        self.draw_form()

    def key1_press(self):
        key1_hw_press()
        

    def key2_press(self):
        key2_hw_press()

    def key3_press(self):
        key3_hw_press()
        

    def set_backlight(self,val):
        global backlight_val
        print("set backlight :"+val)
        backlight_val=int(val)
        pager.ldc_backlight(backlight_val)
        

    def draw_form(self):
        #canvas Frame
        canvfrm = tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)
        self.canvas = tk.Canvas(canvfrm, bg="black", width=pager.LCD_SIZE[0], height=pager.LCD_SIZE[1])        
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        canvfrm.pack(side=tk.TOP, padx=5, pady=5)
        #toolbar Frame
        toolbar = tk.Frame(self.root, bg=self.win_col, height=20)
        tk.Button(toolbar, text="1", command=self.key1_press).pack(side=tk.LEFT, expand=tk.YES)
        tk.Button(toolbar, text="2", command=self.key2_press).pack(side=tk.LEFT, expand=tk.YES)   
        tk.Button(toolbar, text="3", command=self.key3_press).pack(side=tk.RIGHT, expand=tk.YES)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=0)
        toolbar.pack_propagate(False)
        #Scale Frame
        scaleFrm = tk.Frame(self.root, bg=self.win_col, height=20)
        self.blScale=tk.Scale(scaleFrm, to=100, orient=tk.HORIZONTAL,showvalue=0,command=lambda x :self.set_backlight(x))
        self.blScale.set(backlight_val)
        self.blScale.pack(side=tk.TOP, fill=tk.X, padx=2, pady=4)
        scaleFrm.pack(side=tk.BOTTOM, fill=tk.X)
        #scaleFrm.pack_propagate(False)

    def draw_lcd(self,img):
        global tkimg
        tkimg = ImageTk.PhotoImage(img)
        self.canvas.create_image(1,1,anchor=tk.NW,image=tkimg)
        self.canvas.update()
        
    def run(self):
        self.root.mainloop()
#-------- End of Gui Class ---------

#======== Time Thread ========
def draw_image(img):
    global gui
    if play_mode==GUI_PLAY:
        gui.draw_lcd(img)
    elif play_mode==LCD_PLAY:
        pager.lcd_show(img)
    elif play_mode==DUAL_PLAY:        
        pager.lcd_show(img)            
        gui.draw_lcd(img)

def time_thread():
     global exit,pause,humid
     while True:
        tm.sleep(1)
        if exit:
            break
        if pause:
            continue
        if (sensor_id==SENS_HAT) and (humid=='0'):
            weather_update()
        timestr = tm.strftime("%d-%m-%Y  %H:%M:%S")
        img=pager.draw_main(time=timestr,ip_addr=ip_addr,temperture=temper,humidity=humid,pressure=press, desc=sens_dscr)
        draw_image(img)
#-------- End of Time Thread ---------

#======== Cpu Info Thread ========
def cpuInfo_thread():
    global exit,ip_addr
    while True:
        tm.sleep(5)
        if exit:
            break
        ip_addr=ip.get_ip_address("wlan0")
#-------- End of Cpu Info Thread ---------

#======== Weather Thread ======
def weather_update():
    global temper,humid,press,sens_dscr
    if sensor_id==SENS_IN:
       sens_dscr='IN'
       info = sens_in.get_sensor_info()
    elif sensor_id==SENS_WEB:
       sens_dscr='WEB'
       info = wthr.get_weather_info()
    elif sensor_id==SENS_HAT:
       sens_dscr='HAT'
       info = hat.get_sensor_info()
    temper='{:.1f}'.format(info['Temper'])
    humid='{}'.format(info['Humidity'])
    if sensor_id==SENS_IN:
        press='0'
    else:    
        press='{}'.format(info['Pressure'])


def weather_thread(tmout):
    global exit,tm_cnt
    tm_cnt=0
    weather_update()
    while True:          
        if exit:
            break
        tm_cnt += 1
        if tm_cnt>tmout:
            weather_update()
            if exit:
               break            
            tm_cnt=0
        tm.sleep(1)
#-------- End of Weather Thread ---------   

#======== keys =================
def backlight_play():
    global backlight_val,gui
    if backlight_val < 40:
        backlight_val += 10
    else:    
        backlight_val += 20
    backlight_val = (backlight_val//10)*10
    if backlight_val>100:
        backlight_val=3
    pager.ldc_backlight(backlight_val)
    if gui != None:
        gui.blScale.set(backlight_val)

def menu_play():
    global pause,on_menu
    pause = True
    on_menu = True
    menu.reset_select()
    img=pager.get_curr_img()
    img=menu.draw_menu(img)
    draw_image(img)      


def key1_hw_press():
    #print("key1 press")    
    brd.beep()
    global on_menu
    if on_menu:
        img=menu.select_up()
        draw_image(img)
    else:    
        global sensor_id
        sensor_id +=1 
        if sensor_id==SENS_HAT and not hat.exist():
            sensor_id=SENS_IN
        if sensor_id>SENS_HAT:
            sensor_id=SENS_IN
        weather_update()   


def key2_hw_press():
    #print("key2 press")
    brd.beep()
    global on_menu
    if on_menu:
        img=menu.select_down()
        draw_image(img)
    else:    
        global pause
        pause = True
        img=pager.draw_imageSlide()
        draw_image(img)    


def key3_hw_press():
    #print("key3 press")
    brd.beep()   
    global pause,on_menu
    if on_menu:
         on_menu = False
         pause = False
         print('menu sel:'+str(menu.get_select()))
    elif pause:
        pause = False         
    else:
        #backlight_play()
        menu_play()


       

#======== Main Program =========
brd.init()
brd.key1_func = key1_hw_press
brd.key2_func = key2_hw_press
brd.key3_func = key3_hw_press
brd.init_buttons()

hat.init()

if play_mode==GUI_PLAY:
    gui = SimulateGui()
elif play_mode==LCD_PLAY:
    pager.lcd_init()
elif play_mode==DUAL_PLAY:
    gui = SimulateGui()
    pager.lcd_init()

# start time thread
tm_thrd=thrd.Thread(target=time_thread)
tm_thrd.start()
# start lanIp thread
cpu_thrd=thrd.Thread(target=cpuInfo_thread)
cpu_thrd.start()
# start wheather thread
wether_thrd=thrd.Thread(target=weather_thread, args=(60,)) # sec update
wether_thrd.start()

if (play_mode==GUI_PLAY) or (play_mode==DUAL_PLAY):
    gui.run()
    exit=True
    tm_thrd.join()
    print("Program Exit")
elif play_mode==LCD_PLAY:
    while True:
        tm.sleep(5)

brd.close()
pager.lcd_close()
print("End!")
#-------- End of Main Program ---------
