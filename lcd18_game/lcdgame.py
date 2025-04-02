import tkinter as tk
import time as tm
import threading as thrd
import lcdpager as pager
import PIL.ImageTk as ImageTk
import ipaddr as ip
import cpuinfo as cpu
import weather as wthr

exit=False
pause=False
ip_addr="--.--.--.--"
temper="--"
humid="--"

LCD_PLAY=1
GUI_PLAY=2
DUAL_PLAY=3
play_mode=LCD_PLAY

#======== Gui Class =========
class SimulateGui:
    win_col = "pink"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LDC 1.8 (160x128)")
        self.root.config(bg=self.win_col)
        if pager.WINDOWS:
            self.root.attributes('-toolwindow', True) #windows
        self.root.resizable(0,0)
        self.draw_form()

    def key1_press(self):
        global pause
        pause = True
        img=pager.draw_imageSlide()
        draw_image(img)
        

    def key2_press(self):
        pass

    def key3_press(self):
        global pause
        pause = False        
        

    def set_backlight(self,val):
        pager.ldc_backlight(val)
        

    def draw_form(self):
        #canvas Frame
        canvfrm = tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)
        self.canvas = tk.Canvas(canvfrm, bg="black", width=pager.LCD_SIZE[0], height=pager.LCD_SIZE[1])        
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        canvfrm.pack(side=tk.TOP, padx=5, pady=5)
        #toolbar Frame
        toolbar = tk.Frame(self.root, bg=self.win_col, height=20)
        tk.Button(toolbar, text="<", command=self.key1_press).pack(side=tk.LEFT, expand=tk.YES)
        tk.Button(toolbar, text=">", command=self.key2_press).pack(side=tk.LEFT, expand=tk.YES)   
        tk.Button(toolbar, text="ok", command=self.key3_press).pack(side=tk.RIGHT, expand=tk.YES)
        toolbar.pack(side=tk.TOP, fill=tk.X, pady=0)
        toolbar.pack_propagate(False)
        #Scale Frame
        scaleFrm = tk.Frame(self.root, bg=self.win_col, height=20)
        blScale=tk.Scale(scaleFrm, to=100, orient=tk.HORIZONTAL,showvalue=0,command=lambda x :self.set_backlight(x))
        blScale.set(50)
        blScale.pack(side=tk.TOP, fill=tk.X, padx=2, pady=4)
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
     global exit,pause,ip_addr
     while True:
        tm.sleep(1)
        if exit:
            break
        if pause:
            continue
        timestr = tm.strftime("%d-%m-%Y  %H:%M:%S")
        img=pager.draw_main(time=timestr,ip_addr=ip_addr,temperture=temper,humidity=humid)
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
def weather_thread(tmout):
    global exit,tm_cnt,temper,humid
    tm_cnt=0
    info = wthr.get_weather_info()
    temper='{:.1f}'.format(info['Temper'])
    humid='{}'.format(info['Humidity'])
    while True:          
        if exit:
            break
        tm_cnt += 1
        if tm_cnt>tmout:        
            info = wthr.get_weather_info()
            if exit:
               break            
            temper='{:.1f}'.format(info['Temper'])
            humid='{}'.format(info['Humidity'])
            tm_cnt=0
        tm.sleep(1)
#-------- End of Weather Thread ---------   

#======== Main Program =========
if play_mode==GUI_PLAY:
    gui = SimulateGui()
    #img=pager.draw_main()
    #gui.draw_lcd(img)
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
#-------- End of Main Program ---------
