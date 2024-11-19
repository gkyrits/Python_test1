import tkinter as tk
import time as tm
import threading as thrd
import ipaddr as ip

LCD_SIZE = "320x240"
FULL_SCREEN = 1

exit = False

def get_month(date):    
    if date==1:
        return "January"
    elif date==2:
         return "February"
    elif date==3:
         return "March"
    elif date==4:
         return "April"
    elif date==5:
         return "May"
    elif date==6:
         return "June"
    elif date==7:
         return "July"
    elif date==8:
         return "August"
    elif date==9:
         return "September"
    elif date==10:
         return "October"
    elif date==11:
         return "November"
    elif date==12:
         return "December"

def get_weekDay(wday):

    if wday==0:
         return "Monday"
    elif wday==1:
         return "Tuesday"
    elif wday==2:
         return "Wednesday"
    elif wday==3:
         return "Thursday"
    elif wday==4:
         return "Friday"
    elif wday==5:
         return "Saturday"
    elif wday==6:
        return "Sunday"         
          
    
#======== Gui Class =========
class Gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("raspi play v0.1")
        self.root.geometry(LCD_SIZE+'+0+0')
        if(FULL_SCREEN):
              self.root.overrideredirect(1)  
        self.init_clock_window()

    def __str__(self):
        """ description """
        return "Gui Class"        

    def run(self):
        self.root.mainloop()

    def update_clock(self,time):
        time_part = time.split(":")
        main_time = time_part[0]+":"+time_part[1]
        sec_time = ":"+time_part[2]        
        self.clkMain_lbl.config(text=main_time)
        self.clkSec_lbl.config(text=sec_time)        

    def update_date(self,date):
        date_part = date.split("/")
        self.dateMonth_lbl.config(text=get_month(int(date_part[1])))
        self.dateDay_lbl.config(text=date_part[0])
        self.dateYear_lbl.config(text=date_part[2])
        self.dateWeek_lbl.config(text=get_weekDay(int(date_part[3])))

    def update_ethIp(self,IpAddr):
         self.ethIp.config(text=IpAddr)

    def update_wanIp(self,IpAddr):
         self.wanIp.config(text=IpAddr)
       
    def btn_exit(self):
        global exit  
        exit=True
        self.root.destroy()


    def init_clock_window(self):
        #---------------
        #  panel buttons left
        #---------------
        win_col = "light yellow"
        pnl_bt_col = "pink"
        pnlButton =  tk.Frame(self.root, bg=win_col, width=20, padx=1)
        tk.Button(pnlButton,text="1", bg=pnl_bt_col).pack(side=tk.TOP, expand=tk.YES) #Button.width: in text size
        tk.Button(pnlButton,text="2", bg=pnl_bt_col).pack(side=tk.TOP, expand=tk.YES)
        tk.Button(pnlButton,text="3", bg=pnl_bt_col, command=self.btn_exit).pack(side=tk.TOP, expand=tk.YES)
        pnlButton.pack(side=tk.LEFT, fill=tk.Y)
        pnlButton.pack_propagate(False) #enable Frame width=20
        #-------------
        #  panel right
        #-------------
        pnlClock =  tk.Frame(self.root, bg=win_col, relief=tk.GROOVE, borderwidth=2)
        #--panel datetime
        datetm_bg = "light steel blue"
        datetmfrm = tk.Frame(pnlClock, bg=datetm_bg)
        #--panel clock        
        clk_fg = "purple"
        clkFrm = tk.Frame(datetmfrm, bg=datetm_bg, height=70)
        self.clkMain_lbl = tk.Label(clkFrm, text="00:00", fg=clk_fg, bg=datetm_bg, font="Arial 60 bold")
        self.clkMain_lbl.pack(side=tk.LEFT)
        self.clkSec_lbl = tk.Label(clkFrm, text=":00", fg=clk_fg, bg=datetm_bg, font="Arial 30 bold")
        self.clkSec_lbl.pack(side=tk.LEFT, anchor=tk.S)
        clkFrm.pack(side=tk.TOP, fill=tk.X)
        clkFrm.pack_propagate(False) #enable Frame height=70
        #--panel date        
        date_fg = "blue"
        dateFrm = tk.Frame(datetmfrm, bg=datetm_bg, height=40)
        self.dateDay_lbl = tk.Label(dateFrm, text="01", fg=date_fg, bg=datetm_bg, font="Arial 40 bold")
        self.dateDay_lbl.pack(side=tk.LEFT)  
          #----sub panel day/month
        weekMonthFrm = tk.Frame(dateFrm, bg=datetm_bg)
        self.dateWeek_lbl = tk.Label(weekMonthFrm, text="Monday", fg=date_fg, bg=datetm_bg, font="Arial 10 bold")
        self.dateWeek_lbl.pack(side=tk.TOP, anchor=tk.W)        
        self.dateMonth_lbl = tk.Label(weekMonthFrm, text="January", fg=date_fg, bg=datetm_bg, font="Arial 16 bold")
        self.dateMonth_lbl.pack(side=tk.TOP, anchor=tk.W)
        weekMonthFrm.pack(side=tk.LEFT)
          #-------------------  
        self.dateYear_lbl = tk.Label(dateFrm, text="2024", fg=date_fg, bg=datetm_bg, font="Arial 30 bold")
        self.dateYear_lbl.pack(side=tk.LEFT, anchor=tk.S)          
        dateFrm.pack(side=tk.TOP, fill=tk.X, padx=2)
        dateFrm.pack_propagate(False) #enable Frame height=40
        #--close panel datetm
        datetmfrm.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        #--close panel right
        pnlClock.pack(side=tk.TOP, fill=tk.X)
        #------
        # panel bottom 
        #------
        pnlBottom = tk.Frame(self.root, bg=win_col, relief=tk.GROOVE, borderwidth=2)
        #--panel IPinfo
        lanLblFont="Arial 10 bold italic"
        lanIpFont= "Arial 12 bold"
        wanIPcol="green"
        lanIPcol="SlateBlue4"
        IpPnlWidht=130
        IPInfoFrm = tk.Frame(pnlBottom, bg=datetm_bg, width=IpPnlWidht)
          #-----sub panel for Lan info
        lanInfoFrm=tk.Frame(IPInfoFrm,bg=datetm_bg, height=35, width=IpPnlWidht)
        tk.Label(lanInfoFrm,text="Lan:", bg=datetm_bg, fg=lanIPcol, font=lanLblFont).pack(side=tk.TOP, anchor=tk.W)
        self.ethIp = tk.Label(lanInfoFrm,text="255.255.255.255", bg=datetm_bg, fg=lanIPcol, font=lanIpFont)
        self.ethIp.pack(side=tk.TOP, anchor=tk.W)
        lanInfoFrm.pack(side=tk.TOP, anchor=tk.W)
        lanInfoFrm.pack_propagate(False)
          #-----sub panel for Wan info
        wanInfoFrm=tk.Frame(IPInfoFrm,bg=datetm_bg, height=35, width=IpPnlWidht)  
        tk.Label(wanInfoFrm,text="Wan:", bg=datetm_bg, fg=wanIPcol, font=lanLblFont).pack(side=tk.TOP, anchor=tk.W)
        self.wanIp = tk.Label(wanInfoFrm,text="0.0.0.0", bg=datetm_bg, fg=wanIPcol, font=lanIpFont)
        self.wanIp.pack(side=tk.TOP, anchor=tk.W)
        wanInfoFrm.pack(side=tk.TOP, anchor=tk.W)
        wanInfoFrm.pack_propagate(False)
         #--close panel IPinfo
        IPInfoFrm.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        IPInfoFrm.pack_propagate(False) #enable Frame width=100
        #--close panel bottom
        pnlBottom.pack(side=tk.BOTTOM, fill=tk.Y, expand=tk.YES, anchor=tk.W)

        
#======== Time Thread ========

def update_guiDateTime(clk: Gui):
     time_inf = tm.localtime(tm.time())
     #print(time_inf)
     time = "{0:02d}:{1:02d}:{2:02d}".format(time_inf.tm_hour,time_inf.tm_min,time_inf.tm_sec)
     clk.update_clock(time)
     date = "{0:d}/{1:d}/{2:d}/{3:d}".format(time_inf.tm_mday,time_inf.tm_mon,time_inf.tm_year,time_inf.tm_wday)
     clk.update_date(date)     

def time_thread():
     global gui,exit
     while True:
          tm.sleep(1)
          if exit:
               break
          update_guiDateTime(gui)

#======== lanIp Thread ========          
def lanIp_thread():
     global gui,exit
     while True:          
          if exit:
               break
          gui.update_ethIp(ip.get_ip_address("eth0"))
          gui.update_wanIp(ip.get_ip_address("wlan0"))
          if exit:
               break          
          tm.sleep(5)
               
#======== Main ===============
        
gui = Gui()
# start time thread
tm_thrd=thrd.Thread(target=time_thread)
tm_thrd.start()
# start lanIp thread
lan_thrd=thrd.Thread(target=lanIp_thread)
lan_thrd.start()

gui.run()
tm_thrd.join()
lan_thrd.join()

print("End...")
