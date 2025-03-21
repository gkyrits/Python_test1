import tkinter as tk
import time as tm
import threading as thrd
import lcdpager as pager
import PIL.ImageTk as ImageTk
import ipaddr as ip
import cpuinfo as cpu

exit=False
ip_addr="--.--.--.--"

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
        #self.root.attributes('-toolwindow', True) #windows
        self.root.resizable(0,0)
        self.draw_form()

    def draw_form(self):
        #canvas Frame
        canvfrm = tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)
        self.canvas = tk.Canvas(canvfrm, bg="black", width=pager.LCD_SIZE[0], height=pager.LCD_SIZE[1])        
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        canvfrm.pack(side=tk.TOP, padx=10, pady=10)

    def draw_lcd(self,img):
        global tkimg
        tkimg = ImageTk.PhotoImage(img)
        self.canvas.create_image(1,1,anchor=tk.NW,image=tkimg)
        self.canvas.update()
        
    def run(self):
        self.root.mainloop()
#-------- End of Gui Class ---------

#======== Time Thread ========
def time_thread():
     global gui,exit,ip_addr
     while True:
        tm.sleep(1)
        if exit:
            break
        timestr = tm.strftime("%d-%m-%Y  %H:%M:%S")
        img=pager.draw_main(time=timestr,ip_addr=ip_addr)
        if play_mode==GUI_PLAY:
            gui.draw_lcd(img)
        elif play_mode==LCD_PLAY:
            pager.lcd_show(img)
        elif play_mode==DUAL_PLAY:
            pager.lcd_show(img)
            gui.draw_lcd(img)

#-------- End of Time Thread ---------

#======== Cpu Info Thread ========
def cpuInfo_thread():
    global gui,exit,ip_addr
    while True:
        tm.sleep(5)
        if exit:
            break
        ip_addr=ip.get_ip_address("wlan0")
#-------- End of Cpu Info Thread ---------



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

if (play_mode==GUI_PLAY) or (play_mode==DUAL_PLAY):
    gui.run()
    exit=True
    tm_thrd.join()
    print("Program Exit")
elif play_mode==LCD_PLAY:
    while True:
        tm.sleep(5)       
#-------- End of Main Program ---------
