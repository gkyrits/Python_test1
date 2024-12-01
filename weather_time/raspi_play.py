import tkinter as tk
import time as tm
import threading as thrd
import ipaddr as ip
import weather as wthr

LCD_SIZE = "320x240"
FULL_SCREEN = 1

exit = False
wthr_count = 0

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

     def update_weather(self,info):
          if info['Error']=='':
               self.wthr_temper.config(text='{:.1f}°C'.format(info['Temper']))
               self.wthr_descript.config(text=info['Descript'])
               self.wthr_like.config(text='{:.1f}°C'.format(info['Like']))
               self.wthr_humid.config(text='{}%'.format(info['Humidity']))
               self.wthr_press.config(text='{} hPa'.format(info['Pressure']))
               self.wthr_wind.config(text='{} m/s'.format(info['Wind']))
               self.wthr_count.config(text=wthr_count)
         
       
     def btn_exit(self):
        global exit  
        exit=True
        self.root.destroy()


     def keys_panel(self,parent):
        pnl_bt_col = "pink"
        tk.Button(parent,text="1", bg=pnl_bt_col).pack(side=tk.TOP, expand=tk.YES) #Button.width: in text size
        tk.Button(parent,text="2", bg=pnl_bt_col).pack(side=tk.TOP, expand=tk.YES)
        tk.Button(parent,text="3", bg=pnl_bt_col, command=self.btn_exit).pack(side=tk.TOP, expand=tk.YES)


     def clock_panel(self,parent):
        #--panel datetime
        datetm_bg = "light steel blue"
        datetmfrm = tk.Frame(parent, bg=datetm_bg)
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


     def ipInfo_panel(self,parent):
        datetm_bg = "light steel blue"
        lanLblFont="Arial 8 bold italic"
        lanIpFont= "Arial 10 bold"
        wanIPcol="green"
        lanIPcol="SlateBlue4"
        IPheight=30
        IPwidth=100
        IPInfoFrm = tk.Frame(parent, bg=datetm_bg)
          #-----sub panel for Lan info
        lanInfoFrm=tk.Frame(IPInfoFrm,bg=datetm_bg, height=IPheight, width=IPwidth)
        tk.Label(lanInfoFrm,text="Lan:", bg=datetm_bg, fg=lanIPcol, font=lanLblFont).pack(side=tk.TOP, anchor=tk.W)
        self.ethIp = tk.Label(lanInfoFrm,text="0.0.0.0", bg=datetm_bg, fg=lanIPcol, font=lanIpFont, anchor=tk.W)
        self.ethIp.pack(side=tk.TOP, anchor=tk.W)
        lanInfoFrm.pack(side=tk.TOP, anchor=tk.W)
        lanInfoFrm.pack_propagate(False)
          #-----sub panel for Wan info
        wanInfoFrm=tk.Frame(IPInfoFrm,bg=datetm_bg, height=IPheight, width=IPwidth)  
        tk.Label(wanInfoFrm,text="Wan:", bg=datetm_bg, fg=wanIPcol, font=lanLblFont).pack(side=tk.TOP, anchor=tk.W)
        self.wanIp = tk.Label(wanInfoFrm,text="255.255.255.255", bg=datetm_bg, fg=wanIPcol, font=lanIpFont)
        self.wanIp.pack(side=tk.TOP, anchor=tk.W)
        wanInfoFrm.pack(side=tk.TOP, anchor=tk.W)   
        wanInfoFrm.pack_propagate(False)
        #--close panel IPinfo
        IPInfoFrm.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=tk.YES)        


     def weather_panel(self,parent):        
        global img
        wthr_bg = "light steel blue"        
        temperCol="red"  
        infoCol="blue" 
        test_img='13.png'
        img = tk.PhotoImage(file=test_img)        
        wthrFrm=tk.Frame(parent,bg=wthr_bg)
        for row in range(6): # 6 rows
            wthrFrm.rowconfigure(row, weight=1) #resize grid height

        self.wthr_descript=tk.Label(wthrFrm, text="Clear Sky", fg="blue", bg=wthr_bg, font="Arial 10 bold", anchor=tk.W)
        self.wthr_descript.grid(row=0, columnspan=3, sticky=tk.W)

        self.wthr_temper=tk.Label(wthrFrm, text="24°C", fg=temperCol,  bg=wthr_bg, font="Arial 20 bold")
        self.wthr_temper.grid(row=1, columnspan=2, sticky=tk.W)

        self.wthr_image=tk.Label(wthrFrm, image=img,  bg=wthr_bg)
        self.wthr_image.grid(row=1, column=2, sticky=tk.W)

        tk.Label(wthrFrm, text="Feels Like",  bg=wthr_bg, font="Arial 8").grid(row=2, sticky=tk.W)
        tk.Label(wthrFrm, text="Humidity",    bg=wthr_bg, font="Arial 8").grid(row=3, sticky=tk.W)
        tk.Label(wthrFrm, text="Pressure",    bg=wthr_bg, font="Arial 8").grid(row=4, sticky=tk.W)
        tk.Label(wthrFrm, text="Wind",        bg=wthr_bg, font="Arial 8").grid(row=5, sticky=tk.W)

        self.wthr_like=tk.Label(wthrFrm, text="23°C",  fg=infoCol, bg=wthr_bg, font="Arial 8 bold")
        self.wthr_like.grid(row=2, column=1, sticky=tk.W)
        self.wthr_humid=tk.Label(wthrFrm, text="36%",  bg=wthr_bg, fg=infoCol, font="Arial 8 bold")
        self.wthr_humid.grid(row=3, column=1, sticky=tk.W)
        self.wthr_press=tk.Label(wthrFrm, text="1024 hPa",  bg=wthr_bg, fg=infoCol, font="Arial 8 bold")
        self.wthr_press.grid(row=4, column=1,  columnspan=2, sticky=tk.W)
        self.wthr_wind=tk.Label(wthrFrm, text="2.7 m/s",  bg=wthr_bg, fg=infoCol, font="Arial 8 bold")
        self.wthr_wind.grid(row=5, column=1,  columnspan=2, sticky=tk.W)

        self.wthr_count=tk.Label(wthrFrm, text="4",  bg=wthr_bg, font="Arial 8 bold")
        self.wthr_count.grid(row=5, column=3,  columnspan=2, sticky=tk.E)        

        wthrFrm.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=tk.YES)



     def init_clock_window(self):
        #----------------------
        #  panel buttons left
        #----------------------
        win_col = "light yellow"        
        pnlButton =  tk.Frame(self.root, bg=win_col, width=20, padx=1)
        self.keys_panel(pnlButton)
        pnlButton.pack(side=tk.LEFT, fill=tk.Y)
        pnlButton.pack_propagate(False) #enable Frame width=20

        #----------------
        #  panel right
        #----------------
        pnlClock =  tk.Frame(self.root, bg=win_col, relief=tk.GROOVE, borderwidth=2)
        self.clock_panel(pnlClock)
        pnlClock.pack(side=tk.TOP, fill=tk.X)

        #----------------
        # panel bottom 
        #----------------
        pnlBottom = tk.Frame(self.root)
        #--panel IPinfo
        pnlCpuInfo = tk.Frame(pnlBottom, bg=win_col, relief=tk.GROOVE, borderwidth=2)        
        self.ipInfo_panel(pnlCpuInfo)        
        pnlCpuInfo.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, anchor=tk.W)
        #--panel Weather
        weatherFrm = tk.Frame(pnlBottom, bg=win_col, relief=tk.GROOVE, borderwidth=2)
        self.weather_panel(weatherFrm)
        weatherFrm.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, anchor=tk.W)
        #--close panel Bottom  
        pnlBottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=tk.YES)

        
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


#======== Weather Thread ======
def weather_thread():
     global gui,exit,wthr_count
     while True:          
          if exit:
               break
          wthr_count += 1
          info = wthr.get_weather_info()
          if exit:
               break          
          gui.update_weather(info)
          tm.sleep(60)


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
# start lanIp thread
wether_thrd=thrd.Thread(target=weather_thread)
wether_thrd.start()

gui.run()
tm_thrd.join()
lan_thrd.join()
wether_thrd.join()

print("End...")
