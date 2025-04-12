import tkinter as tk
import time as tm
import threading as thrd
import ipaddr as ip
import cpuinfo as cpu
import weather as wthr
import battery as batt
import aht10sense as sense1
import si7021sense as sense2
import mpl3115sense as sense3
#import matplotgraph as plot
import simplegraph as plot
import repository as repo
import subprocess as proc
import sys
import os

LCD_SIZE = "320x240"
FULL_SCREEN = 0

exit = False
infoWin = False
wthr_count = 0
wthr_pressure = 1013  #for set MPL3115 sea pressure
sense_need_update=False

EN=0
GR=1
lang=GR

monthLst = ['January','February','March','April','May','June','July','August','September','October','November','December']
monthLst_gr=['Ιανουάριος','Φεβρουάριος','Μάρτιος','Απρίλιος','Μάιος','Ιούνιος','Ιούλιος','Αύγουστος','Σεπτέμβριος','Οκτώβριος','Νοέμβριος','Δεκέμβριος']
weekLst = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
weekLst_gr = ['Δευτέρα','Τρίτη','Τετάρτη','Πέμπτη','Παρασκευή','Σάββατο','Κυριακή']

today_lst = ['(Today)','(Σήμερα)']
tomorrow_lst = ['(Tomorrow)','(Αύριο)']
temper_lst = ['Temperature','Θερμοκρασία']
feel_lst = ['Feels Like','Αίσθηση']
humidity_lst = ['Humidity','Υγρασία']       
pressure_lst = ['Pressure','Πίεση']
altitude_lst = ['Altitude','Υψόμετρο']
wind_lst = ['Wind','Άνεμος']


def get_month(date):    
    if lang==EN:
        return monthLst[date-1]
    else:
        return monthLst_gr[date-1]

def get_weekDay(wday):
    if lang==EN:
        return weekLst[wday]
    else:
        return weekLst_gr[wday]      

def get_windDir(deg):
    if deg<=22 or deg>337:
        return "B"
    elif deg<=67 and deg>22:
        return "ΒΔ"
    elif deg<=112 and deg>67:
        return "Δ"
    elif deg<=157 and deg>112:
        return "NΔ"
    elif deg<=202 and deg>157:
        return "N"
    elif deg<=247 and deg>202:
        return "NA"
    elif deg<=292 and deg>247:
        return "A"
    elif deg<=337 and deg>292:
        return "BA"
    else:
        return "?"
    
          
icon_map_day = {200:14,201:14,202:14,210:15,211:15,212:15,221:15,230:14,231:14,232:14,
                300:12,301:12,310:12,302:10,311:10,312:10,313:10,314:10,321:10,
                500:12,501:10,520:11,502:10,503:11,521:11,504:25,522:25,531:25,511:20,
                611:20,612:20,613:20,615:20,616:20,600:18,612:20,601:24,600:24,612:24,620:18,602:16,621:17,622:17,
                701:9,711:9,721:9,731:9,741:9,751:9,761:9,762:9,771:9,781:14,
                800:2,801:3,802:4,803:6,804:7}
icon_night_map = {15:33,13:32,19:35,24:34,3:27,4:28,6:30,2:26}


def bind_tree(widget, event, callback):
    widget.bind(event, callback)
    for child in widget.children.values():
        bind_tree(child, event, callback)


def forecast_find_day(info,day):
        info_range = [0,0]
        item_cnt=info['Items']        
        if day>0:
            bay_cnt=0
            for x in range(item_cnt):
                 if (info['List'][x]['Hour']=='00'):
                     bay_cnt += 1
                     if bay_cnt==day:
                        info_range[0]=x
                        break                         
        for x in range(info_range[0]+1,item_cnt):
            if (info['List'][x]['Hour']=='00'):
                info_range[1]=x
                break
        if(info_range[1]==0):
            info_range[1]=item_cnt-1
        return info_range         
    
#======== Gui Class =========
class Gui:
     def __init__(self):
        self.root = tk.Tk()
        self.root.title("raspi play v0.1")
        self.root.geometry(LCD_SIZE+'+0+0')
        if(FULL_SCREEN):
              self.root.overrideredirect(1)
        self.root.config(cursor='cross')
        self.nightTime=False
        self.IPInfoFrm=None
        self.SensorFrm=None
        self.sense_id=-1        
        self.wthrFrm_on=True
        self.frcst_tmout=None
        self.smlimg = [None,None,None,None,None,None,None,None]
        self.init_clock_window()

     def __str__(self):
        """ description """
        return "Gui Class"

     #events-----------------------
     def buttonPanel_enter(self,e):
        print('Enter event!')
        self.pnlButton.configure(width=20)

     def buttonPanel_leave(self,e):
        print('Leave event!')
        self.pnlButton.configure(width=4)

     def clockPanel_dblClick(self,e):
        #print('Clock click! :%s' % e.widget)
        #self.__info_window('Clock click!')
        self.graph_window()

     def sensePanel_dblClick(self,e):
        #print('Info click! :%s' % e.widget)
        #self.__info_window('Info click!')
        self.sensePanel_nextShow()

     def weatherPanel_dblClick(self,e):
        #print('Weather click! :%s' % e.widget)
        #self.__info_window('Weather click!')       
        self.weatherPanel_change()

     def key1_press(self):
        print('Key1 press!')     
        #self.__info_window('Key1 press!')
        #self.root.after(10,self.__info_window,'Key1 press!')
        self.root.after(10,self.radio_play)

     def key2_press(self):
        print('Key2 press!')
        #self.__info_window('Key2 press!')
        self.root.after(10,self.__info_window,'Key2 press!')

     def key3_press(self):
        print('Key3 press! - Exit')
        #self.btn_exit()
        self.root.after(10,self.btn_exit)

    #-----------------------------    
     def run(self):
        self.root.mainloop()

     def __set_modal(self,win): #'__' means private
        win.wait_visibility()
        win.grab_set()
        win.wait_window()
        win.grab_release()        

     def __info_window(self,info):
         global infoWin
         if infoWin:
            return
         infoWin=True
         win=tk.Toplevel(bg="green")
         win.geometry('220x80+50+80')
         win.overrideredirect(1)
         bg_col="yellow green"
         frm=tk.Frame(win, bg=bg_col, relief=tk.GROOVE, borderwidth=2)
         tk.Label(frm,text=info, bg=bg_col, font='bold').pack(side=tk.TOP)
         tk.Button(frm,text="Ok", command=win.destroy).place(relx=0.5, rely=0.6, relheight=0.4, relwidth=0.5, anchor=tk.CENTER)
         frm.pack(padx=5, pady=5, fill=tk.BOTH, expand=tk.YES)
         tmout=thrd.Timer(10, lambda :win.destroy())
         tmout.start()
         self.__set_modal(win)         
         tmout.cancel()   
         infoWin=False
         
     def radio_play(self):
         rel_radio_path='/../radioPlayer'
         path = os.getcwd()+rel_radio_path
         sys.path.insert(0,path)
         try:
            from radioplayer import radio_player
            radio_player(rel_radio_path)
         except:
            print('fail run radio_player')
            return   
         

     def graph_window(self):
         win=tk.Toplevel()
         win.geometry(LCD_SIZE+'+0+0')
         win.overrideredirect(1)
         plot.draw_form(win)         


     def update_clock(self,time):
        time_part = time.split(":")
        main_time = time_part[0]+":"+time_part[1]
        sec_time = ":"+time_part[2]        
        self.clkMain_lbl.config(text=main_time)
        self.clkSec_lbl.config(text=sec_time)
        h_time = int(time_part[0])
        if (h_time>=20) or (h_time<=6):
            self.nightTime=True
        else:
            self.nightTime=False


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

     def update_cpu(self,usage,temper):
         if usage != '':
            self.cpuUsage.config(text='{} %'.format(usage))
         else:
            self.cpuUsage.config(text='')
         self.cpuTemp.config(text='{}'.format(temper))

     def update_battery(self,percent,current):
         if percent!=0:
            self.Batt.config(text='{:4.1f} %'.format(percent))
            self.Curr.config(text='{:5.3f} A'.format(current))
         else:
            self.Batt.config(text='')
            self.Curr.config(text='')
                
         

     def update_weather(self,info):
          if info['Error']=='':               
               self.wthr_temper.config(text='{:.1f}'.format(info['Temper']))
               self.wthr_descript.config(text=info['Descript'])
               self.wthr_like.config(text='{:.1f}°C'.format(info['Like']))
               self.wthr_humid.config(text='{} %'.format(info['Humidity']))
               self.wthr_press.config(text='{} hPa'.format(info['Pressure']))
               self.wthr_wind.config(text='{} m/s'.format(info['Wind']))
               self.wthr_windDir.config(text=get_windDir(info['WindDeg']))
               self.wthr_id.config(text='{}-{}'.format(info['Id'],info['Clouds']))
               self.wthr_count.config(text=wthr_count)
               icon_num=icon_map_day[info['Id']]
               if self.nightTime :
                  if icon_num in icon_night_map.keys():
                     icon_num=icon_night_map[icon_num]
               icon_file='icons/'+str(icon_num)+'.png'
               self.img=tk.PhotoImage(file=icon_file)
               self.wthr_image.config(image=self.img)


     def update_sensor(self,info):
        print('update_sensor...')
        if not self.senseinfo_active():
            return
        sense_txt='SENSOR '+str(self.sense_id)
        self.room_sensor.config(text=sense_txt)
        self.room_temper.config(text='{:.1f}'.format(info['Temperature']))
        if (self.sense_id==1) or (self.sense_id==2):
            self.room_humid.config(text='{} %'.format(info['Humidity']))
        elif self.sense_id==3:
            self.room_press.config(text='{:.1f} hPa'.format(info['Pressure']))
            self.room_altit.config(text='{:.1f} m'.format(info['Altitude']))
         
       
     def btn_exit(self):
        global exit  
        exit=True
        self.root.destroy()


     def keys_panel(self,parent):
        pnl_bt_col = "pink"
        tk.Button(parent,text="1", bg=pnl_bt_col, command=self.key1_press).pack(side=tk.TOP, expand=tk.YES) #Button.width: in text size
        tk.Button(parent,text="2", bg=pnl_bt_col, command=self.key2_press).pack(side=tk.TOP, expand=tk.YES)
        tk.Button(parent,text="3", bg=pnl_bt_col, command=self.key3_press).pack(side=tk.TOP, expand=tk.YES)


     #-----------------------------------------------------------------------------
     #-----------------------------------------------------------------------------
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
        dateFrm.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        dateFrm.pack_propagate(False) #enable Frame height=40
        #--close panel datetm
        datetmfrm.pack(side=tk.TOP, padx=self.pnlPad, pady=self.pnlPad, fill=tk.X)         


     #-----------------------------------------------------------------------------
     #-----------------------------------------------------------------------------
     def ipInfo_panel(self,parent):
        datetm_bg = "light steel blue"
        lanLblFont="Arial 8 bold italic"
        lanIpFont= "Arial 10 bold"
        wanIPcol="green"
        lanIPcol="SlateBlue4"
        cpuLblFont="Arial 8"
        cpuValFont="Arial 8 bold"
        cpuCol="Blue4"        
        IPheight=30
        IPwidth=100
        self.IPInfoFrm = tk.Frame(parent, bg=datetm_bg)
          #-----sub panel for Lan info
        lanInfoFrm=tk.Frame(self.IPInfoFrm,bg=datetm_bg, height=IPheight, width=IPwidth)
        tk.Label(lanInfoFrm,text="Lan:", bg=datetm_bg, fg=lanIPcol, font=lanLblFont).pack(side=tk.TOP, anchor=tk.W)
        self.ethIp = tk.Label(lanInfoFrm,text="--.--.--.--", bg=datetm_bg, fg=lanIPcol, font=lanIpFont, anchor=tk.W)
        self.ethIp.pack(side=tk.TOP, anchor=tk.W)
        lanInfoFrm.pack(side=tk.TOP, anchor=tk.W)
        lanInfoFrm.pack_propagate(False)
          #-----sub panel for Wan info
        wanInfoFrm=tk.Frame(self.IPInfoFrm,bg=datetm_bg, height=IPheight, width=IPwidth)  
        tk.Label(wanInfoFrm,text="Wan:", bg=datetm_bg, fg=wanIPcol, font=lanLblFont).pack(side=tk.TOP, anchor=tk.W)
        self.wanIp = tk.Label(wanInfoFrm,text="--.--.--.--", bg=datetm_bg, fg=wanIPcol, font=lanIpFont)
        self.wanIp.pack(side=tk.TOP, anchor=tk.W)
        wanInfoFrm.pack(side=tk.TOP, anchor=tk.W)   
        wanInfoFrm.pack_propagate(False)
          #----sub panel cpu/batt info
        cpuInfoFrm=tk.Frame(self.IPInfoFrm,bg=datetm_bg, width=IPwidth)
        for row in range(4): # 4 rows
            cpuInfoFrm.rowconfigure(row, weight=1) #resize grid height                
        tk.Label(cpuInfoFrm,text="usage", bg=datetm_bg, font=cpuLblFont).grid(row=0, column=0, sticky=tk.W)
        self.cpuUsage=tk.Label(cpuInfoFrm,text="--%", bg=datetm_bg, fg=cpuCol, font=cpuValFont)
        self.cpuUsage.grid(row=0, column=1, sticky=tk.W)
        tk.Label(cpuInfoFrm,text="temper", bg=datetm_bg, font=cpuLblFont).grid(row=1, column=0, sticky=tk.W)
        self.cpuTemp=tk.Label(cpuInfoFrm,text="--", bg=datetm_bg, fg=cpuCol, font=cpuValFont)
        self.cpuTemp.grid(row=1, column=1, sticky=tk.W)
        tk.Label(cpuInfoFrm,text="Batt", bg=datetm_bg, font=cpuLblFont).grid(row=2, column=0, sticky=tk.W)
        self.Batt=tk.Label(cpuInfoFrm,text="--%", bg=datetm_bg, fg=cpuCol, font=cpuValFont)
        self.Batt.grid(row=2, column=1, sticky=tk.W)
        tk.Label(cpuInfoFrm,text="curr", bg=datetm_bg, font=cpuLblFont).grid(row=3, column=0, sticky=tk.W)
        self.Curr=tk.Label(cpuInfoFrm,text="-.---", bg=datetm_bg, fg=cpuCol, font=cpuValFont)
        self.Curr.grid(row=3, column=1, sticky=tk.W)
        cpuInfoFrm.pack(side=tk.TOP, anchor=tk.W,pady=4)   
        cpuInfoFrm.pack_propagate(False)
        #--close panel IPinfo        
        self.IPInfoFrm.pack(side=tk.LEFT, padx=self.pnlPad, pady=self.pnlPad, fill=tk.BOTH, expand=tk.YES)        


     def senseInfo_panel(self,parent):
        sense_bg = "light steel blue"        
        tempLblCol= "SlateBlue4"
        temperCol="purple"
        humidCol="dark green"
        altitCol="blue1" 
        sense_txt='SENSOR '+str(self.sense_id)
        if self.sense_id==3:
            rows=6
        else:
            rows=4    
        self.SensorFrm = tk.Frame(parent, bg=sense_bg)
        #---SensorFrm        
        for row in range(rows): # 4 rows
            self.SensorFrm.rowconfigure(row, weight=1) #resize grid height
        self.room_sensor = tk.Label(self.SensorFrm,text=sense_txt, bg=sense_bg, fg="blue", font="Arial 7")
        self.room_sensor.grid(row=0)
        tk.Label(self.SensorFrm,text=temper_lst[lang], bg=sense_bg, fg=tempLblCol, font="Arial 8 bold").grid(row=1, sticky=tk.W)
        #-temper frame
        temperFrm=tk.Frame(self.SensorFrm,bg=sense_bg)
        tk.Label(temperFrm, text=" ", fg=temperCol,  bg=sense_bg, font="Arial 20 bold").pack(side=tk.LEFT)
        self.room_temper=tk.Label(temperFrm, text="--.-", fg=temperCol,  bg=sense_bg, font="Arial 20 bold")
        self.room_temper.pack(side=tk.LEFT)
        tk.Label(temperFrm, text="°C", fg=temperCol,  bg=sense_bg, font="Arial 12 bold").pack(side=tk.TOP)
        temperFrm.grid(row=2, sticky=tk.E)
        if (self.sense_id==1) or (self.sense_id==2):
            #-Humidity
            tk.Label(self.SensorFrm,text=humidity_lst[lang], bg=sense_bg, fg=tempLblCol, font="Arial 8 bold").grid(row=3, sticky=tk.W)
            self.room_humid=tk.Label(self.SensorFrm,text="--%", bg=sense_bg, fg=humidCol, font="Arial 14 bold")
            self.room_humid.grid(row=4, sticky=tk.E)
        elif self.sense_id==3:
            tk.Label(self.SensorFrm,text=pressure_lst[lang], bg=sense_bg, fg=tempLblCol, font="Arial 8 bold").grid(row=3, sticky=tk.W)
            self.room_press=tk.Label(self.SensorFrm,text="----.- hPa", bg=sense_bg, fg=humidCol, font="Arial 10 bold")
            self.room_press.grid(row=4, sticky=tk.E)
            tk.Label(self.SensorFrm,text=altitude_lst[lang], bg=sense_bg, fg=tempLblCol, font="Arial 8 bold").grid(row=5, sticky=tk.W)
            self.room_altit=tk.Label(self.SensorFrm,text="- m", bg=sense_bg, fg=altitCol, font="Arial 10 bold")
            self.room_altit.grid(row=6, sticky=tk.E)            
        #--close panel SensorFrm
        self.SensorFrm.pack(side=tk.LEFT, padx=self.pnlPad, pady=self.pnlPad, fill=tk.BOTH, expand=tk.YES) 
        

     def sensePanel_change(self):
        if self.IPInfoFrm != None:
            self.IPInfoFrm.pack_forget()
            self.IPInfoFrm=None
            self.senseInfo_panel(self.pnlSenseInfo)
            bind_tree(self.SensorFrm,'<Button-1>',self.sensePanel_dblClick)            
        else:
            if self.SensorFrm !=None:
                self.SensorFrm.pack_forget()
                self.SensorFrm=None  
            self.ipInfo_panel(self.pnlSenseInfo)
            bind_tree(self.IPInfoFrm,'<Button-1>',self.sensePanel_dblClick)


     def sensePanel_nextShow(self):
        global sense_need_update
        if self.sense_id < 0:
            self.sense_id=1            
            self.senseInfo_panel(self.pnlSenseInfo)
            sense_need_update=True
        elif self.sense_id == 0:
            self.sense_id=1            
            self.sensePanel_change()
            sense_need_update=True
        elif self.sense_id == 1:
            self.sense_id=2
            sense_need_update=True
        elif self.sense_id == 2:
            self.sense_id=3
            self.SensorFrm.pack_forget()
            self.senseInfo_panel(self.pnlSenseInfo)
            bind_tree(self.SensorFrm,'<Button-1>',self.sensePanel_dblClick)            
            sense_need_update=True
        elif self.sense_id == 3:
            self.sense_id=0
            self.sensePanel_change()  


     def sensePanel_visible(self,visible):        
        if not visible:
            if self.IPInfoFrm != None:
                self.IPInfoFrm.pack_forget()
                self.IPInfoFrm=None
            if self.SensorFrm !=None:
                self.SensorFrm.pack_forget()
                self.SensorFrm=None
            self.pnlSenseInfo.pack_forget()
        if visible:
            self.sense_id=-1
            self.sensePanel_nextShow()            
            self.weatherFrm.pack_forget()
            self.pnlSenseInfo.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, anchor=tk.W)                        
            self.weatherFrm.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, anchor=tk.W)
            bind_tree(self.pnlSenseInfo,'<Button-1>',self.sensePanel_dblClick)


     def cpuinfo_active(self):
        if self.IPInfoFrm != None:
            return True
        else:
            return False
        
     def senseinfo_active(self):
        if self.SensorFrm != None:
            return True
        else:
            return False    

     #-----------------------------------------------------------------------------
     #----------------------------------------------------------------------------- 
     def weather_panel(self,parent):                
        wthr_bg = "light steel blue"        
        temperCol="red"  
        humidCol="red4"
        infoCol="blue" 
        self.img = tk.PhotoImage(file='icons/13.png')        
        self.wthrFrm=tk.Frame(parent,bg=wthr_bg)
        for row in range(6): # 6 rows
            self.wthrFrm.rowconfigure(row, weight=1) #resize grid height

        self.wthr_descript=tk.Label(self.wthrFrm, text="Clear Sky", fg="blue", bg=wthr_bg, font="Arial 10 bold", anchor=tk.W)
        self.wthr_descript.grid(row=0, columnspan=4, sticky=tk.W)
        
        temperFrm=tk.Frame(self.wthrFrm,bg=wthr_bg)
        self.wthr_temper=tk.Label(temperFrm, text="24", fg=temperCol,  bg=wthr_bg, font="Arial 20 bold")
        self.wthr_temper.pack(side=tk.LEFT)
        tk.Label(temperFrm, text="°C", fg=temperCol,  bg=wthr_bg, font="Arial 12 bold").pack(side=tk.TOP)
        temperFrm.grid(row=1, columnspan=2, sticky=tk.W)

        self.wthr_image=tk.Label(self.wthrFrm, image=self.img,  bg=wthr_bg, anchor=tk.W)
        self.wthr_image.grid(row=1, column=2,  columnspan=2, rowspan=3, sticky=tk.W)

        tk.Label(self.wthrFrm, text=feel_lst[lang],  bg=wthr_bg, font="Arial 8").grid(row=2, sticky=tk.W)
        tk.Label(self.wthrFrm, text=humidity_lst[lang],    bg=wthr_bg, font="Arial 8").grid(row=3, sticky=tk.W)
        tk.Label(self.wthrFrm, text=pressure_lst[lang],    bg=wthr_bg, font="Arial 8").grid(row=4, sticky=tk.W)
        tk.Label(self.wthrFrm, text=wind_lst[lang],        bg=wthr_bg, font="Arial 8").grid(row=5, sticky=tk.W)

        self.wthr_like=tk.Label(self.wthrFrm, text="23°C",  fg=infoCol, bg=wthr_bg, font="Arial 8 bold")
        self.wthr_like.grid(row=2, column=1, sticky=tk.W)
        self.wthr_humid=tk.Label(self.wthrFrm, text="36%",  bg=wthr_bg, fg=humidCol, font="Arial 9 bold")
        self.wthr_humid.grid(row=3, column=1, sticky=tk.W)
        self.wthr_press=tk.Label(self.wthrFrm, text="1024 hPa",  bg=wthr_bg, fg=infoCol, font="Arial 8 bold")
        self.wthr_press.grid(row=4, column=1,  columnspan=2, sticky=tk.W)
        self.wthr_wind=tk.Label(self.wthrFrm, text="2.7 m/s",  bg=wthr_bg, fg=infoCol, font="Arial 8 bold")
        self.wthr_wind.grid(row=5, column=1,  sticky=tk.W)
        self.wthr_windDir=tk.Label(self.wthrFrm, text="NA",  bg=wthr_bg, fg=infoCol, font="Arial 8 bold")
        self.wthr_windDir.grid(row=5, column=2,  sticky=tk.W)        

        self.wthr_count=tk.Label(self.wthrFrm, text="4",  bg=wthr_bg, font="Arial 8 bold")
        self.wthr_count.grid(row=5, column=3,  sticky=tk.E) 
        self.wthr_id=tk.Label(self.wthrFrm, text="800",  bg=wthr_bg, font="Arial 6 bold")
        self.wthr_id.grid(row=4, column=3,  sticky=tk.E)

        self.wthrFrm.pack(side=tk.LEFT, padx=self.pnlPad, pady=self.pnlPad, fill=tk.BOTH, expand=tk.YES)


     def forecast_print(self,parent,prnt_bg,info,day):
        temperCol="purple"
        humidCol="dark green"
        windCol="green"
        pressCol="blue"
        #for x in range(6):
        #    info_rng=forecast_find_day(info,x)
        #    print(info_rng)
        info_rng=forecast_find_day(info,day)
        print(info_rng)
        for row in range(7): # 7 rows
            parent.rowconfigure(row, weight=1) #resize grid height
        for col in range(9): # 9 rows
            parent.columnconfigure(col, weight=1) #resize grid height            
        infodate=info['List'][info_rng[0]]['Date']
        #get epoch time
        datepart=infodate.split('-')
        epoch_time= repo.get_epoch(int(datepart[0]),int(datepart[1]),int(datepart[2]),0,0)
        date=tm.localtime(epoch_time)
        wday=date.tm_wday
        daytxt=get_weekDay(wday)+tm.strftime(' %d-%m-%Y',date)
        if day==0:
            daytxt= today_lst[lang]+' '+daytxt
        elif day==1:
            daytxt= tomorrow_lst[lang]+' '+daytxt
        else:
            daytxt='(+'+str(day)+') '+daytxt
        tk.Label(parent, text=daytxt, bg=prnt_bg, fg=pressCol, font="Arial 8 bold").grid(row=0, columnspan=9)
        tk.Label(parent, text='Hr',     bg=prnt_bg, font="Arial 8").grid(row=1, sticky=tk.W)
        #tk.Label(parent, text='Icon',     bg=prnt_bg, font="Arial 8").grid(row=2, sticky=tk.W)
        tk.Label(parent, text='°C',   bg=prnt_bg, font="Arial 8").grid(row=3, sticky=tk.W)
        tk.Label(parent, text='%', bg=prnt_bg, font="Arial 8").grid(row=4, sticky=tk.W)
        tk.Label(parent, text='hPa', bg=prnt_bg, font="Arial 8").grid(row=5, sticky=tk.W)
        tk.Label(parent, text='m/s',     bg=prnt_bg, font="Arial 8").grid(row=6, sticky=tk.W)
        for idx in range(info_rng[0],info_rng[1]):
            col=idx-info_rng[0]
            hour = info['List'][idx]['Hour']+':'
            tk.Label(parent, text=hour,  bg=prnt_bg, font="Arial 8").grid(row=1, column=col+1)
            icon_num=icon_map_day[info['List'][idx]['Id']]
            if (hour>='20:') or (hour<='06:'):
                if icon_num in icon_night_map.keys():
                    icon_num=icon_night_map[icon_num]
            icon_file='small_icons/'+str(icon_num)+'.png'
            self.smlimg[col] = tk.PhotoImage(file=icon_file)
            imgLbl=tk.Label(parent, image=self.smlimg[col],  bg=prnt_bg)
            imgLbl.grid(row=2, column=col+1)
            if idx==info_rng[0]:
                self.frcstBack=imgLbl
            if idx==info_rng[1]-1:
                self.frcstForw=imgLbl    
            temper='{:.1f}'.format(info['List'][idx]['Temper'])
            tk.Label(parent, text=temper,  bg=prnt_bg, fg=temperCol, font="Arial 8 bold").grid(row=3, column=col+1, sticky=tk.W)
            humid='{}'.format(info['List'][idx]['Humidity'])
            tk.Label(parent, text=humid,  bg=prnt_bg, fg=humidCol, font="Arial 8 bold").grid(row=4, column=col+1, sticky=tk.W)
            press='{}'.format(info['List'][idx]['Pressure'])
            tk.Label(parent, text=press,  bg=prnt_bg, fg=pressCol, font="Arial 8").grid(row=5, column=col+1, sticky=tk.W)
            wind='{:.1f}'.format(info['List'][idx]['Wind'])
            windDeg=get_windDir(info['List'][idx]['WindDeg'])
            tk.Label(parent, text=wind+windDeg, bg=prnt_bg, fg=windCol, font="Arial 8").grid(row=6, column=col+1, sticky=tk.W)


     def forcast_next_event(self,forw):
        print('Next '+str(forw))
        if forw:
            self.frcst_day += 1
            if self.frcst_day > 5:
                self.frcst_day=5
        else:
            self.frcst_day -= 1
            if self.frcst_day < 0:
                self.frcst_day=0            
        self.forcstFrm.pack_forget()
        self.forecast_panel(self.weatherFrm,self.frcst_info)


     #bind back-force image ivents
     def bind_next(self):
        self.frcstBack.bind('<Button-1>', lambda e, forw=False : self.forcast_next_event(forw))
        self.frcstForw.bind('<Button-1>', lambda e, forw=True : self.forcast_next_event(forw))


     def forecast_panel(self,parent,info):
        wthr_bg = "light steel blue"
        self.forcstFrm=tk.Frame(parent,bg=wthr_bg)        
        self.forecast_print(self.forcstFrm,wthr_bg,info,self.frcst_day)
        self.forcstFrm.pack(side=tk.LEFT, padx=self.pnlPad, pady=self.pnlPad, fill=tk.BOTH, expand=tk.YES)
        bind_tree(self.forcstFrm,'<Button-1>',self.weatherPanel_dblClick)        
        self.bind_next()
        if self.frcst_tmout != None:
            self.root.after_cancel(self.frcst_tmout)        
        self.frcst_tmout=self.root.after(30000,self.weatherPanel_change)


     def weatherPanel_change(self):
        if self.wthrFrm_on:
           print('get forcast info') 
           self.frcst_info = wthr.get_forecast_info()
           if self.frcst_info['Error'] != '':
               return
           self.sensePanel_visible(False)
           self.wthrFrm.pack_forget()
           self.wthrFrm_on=False
           #get current hour
           hour =  tm.localtime(tm.time()).tm_hour
           if hour < 20:
               self.frcst_day=0
           else:
               self.frcst_day=1
           self.forecast_panel(self.weatherFrm,self.frcst_info)
        else:
           if self.frcst_tmout != None:
               self.root.after_cancel(self.frcst_tmout)
           self.frcst_tmout=None    
           self.forcstFrm.pack_forget()
           self.forcstFrm=None           
           self.sensePanel_visible(True)
           self.wthrFrm.pack(side=tk.LEFT, padx=self.pnlPad, pady=self.pnlPad, fill=tk.BOTH, expand=tk.YES)
           self.wthrFrm_on=True
     
     #-----------------------------------------------------------------------------
     #-----------------------------------------------------------------------------
     def init_clock_window(self):
        self.pnlPad=3  #default panel padx, pady
        #----------------------
        #  panel buttons left
        #----------------------
        win_col = "light yellow"
        btn_col = "sky blue"
        self.pnlButton =  tk.Frame(self.root, bg=btn_col, width=20, padx=1)
        self.keys_panel(self.pnlButton)
        self.pnlButton.pack(side=tk.LEFT, fill=tk.Y)
        self.pnlButton.pack_propagate(False) #enable Frame width=20
        self.pnlButton.bind('<Enter>',self.buttonPanel_enter)
        self.pnlButton.bind('<Leave>',self.buttonPanel_leave)
        self.buttonPanel_leave(None)

        #----------------
        #  panel right
        #----------------
        pnlClock =  tk.Frame(self.root, bg=win_col, relief=tk.GROOVE, borderwidth=2)
        self.clock_panel(pnlClock)
        pnlClock.pack(side=tk.TOP, fill=tk.X)
        bind_tree(pnlClock,'<Button-1>',self.clockPanel_dblClick)

        #----------------
        # panel bottom 
        #----------------
        pnlBottom = tk.Frame(self.root)
        #--panel Senseinfo
        self.pnlSenseInfo = tk.Frame(pnlBottom, bg=win_col, relief=tk.GROOVE, borderwidth=2)
        self.sensePanel_nextShow()
        self.pnlSenseInfo.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, anchor=tk.W)
        bind_tree(self.pnlSenseInfo,'<Button-1>',self.sensePanel_dblClick)

        #--panel Weather
        self.weatherFrm = tk.Frame(pnlBottom, bg=win_col, relief=tk.GROOVE, borderwidth=2)
        self.weather_panel(self.weatherFrm)
        self.weatherFrm.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, anchor=tk.W)
        bind_tree(self.weatherFrm,'<Button-1>',self.weatherPanel_dblClick)
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
def weather_thread(tmout):
     global gui,exit,wthr_count,wthr_pressure
     tm_cnt=0
     wthr_count=1
     info = wthr.get_weather_info()
     wthr_pressure = info['Pressure'] 
     gui.update_weather(info)
     while True:          
          if exit:
               break
          tm_cnt += 1
          if tm_cnt>tmout:
            wthr_count += 1
            info = wthr.get_weather_info()
            wthr_pressure = info['Pressure']
            if exit:
               break            
            gui.update_weather(info)            
            tm_cnt=0
          tm.sleep(1)


#======== Sensor Thread ======

def update_mpl1315_seaPressure(info):
    global wthr_pressure
    seaPress = info['SeaPressure']
    if seaPress != wthr_pressure:
         sense3.set_sea_pressure(wthr_pressure)
         print('Update mpl1315 sea pressure : %d' %wthr_pressure)

def read_sensors_info():
    print('*read_sensors_info*')
    repo.info['sens1'] = sense1.get_sensor_info()
    repo.info['sens2'] = sense2.get_sensor_info()
    repo.info['sens3'] = sense3.get_sensor_info()    
    update_mpl1315_seaPressure(repo.info['sens3'])
    repo.info['web'] = wthr.get_small_info()
    repo.save_info_binary()

def get_sensors_info():
    global gui
    if gui.sense_id==1:
        return repo.info['sens1']
    elif gui.sense_id==2:
        return repo.info['sens2']
    elif gui.sense_id==3:
        return repo.info['sens3']    
    else:
        return repo.info['sens1']

def sensor_thread(tmout):
    global gui,exit,sense_need_update
    sense_tm_cnt=0
    read_sensors_info()
    info = get_sensors_info()
    gui.update_sensor(info)
    while True:          
        if exit:
            break
        sense_tm_cnt += 1        
        if sense_tm_cnt>tmout:
            read_sensors_info()
            if exit:
               break             
            info = get_sensors_info()           
            gui.update_sensor(info)
            sense_tm_cnt=0
        if sense_need_update:
            info = get_sensors_info()
            gui.update_sensor(info)
            sense_need_update=False
        tm.sleep(1)


#======== lanIp Thread ========          
def cpuInfo_thread():
     global gui,exit
     battery = batt.INA219()
     while True:          
          if exit:
               break
          if not gui.cpuinfo_active():
              tm.sleep(1)
              continue
          #print('get cpu info...')
          cpu_usage=cpu.get_cpuUsage()
          if exit:
               break
          cpu_temp=cpu.get_cpuTemp()
          if exit:
               break          
          gui.update_cpu(cpu_usage,cpu_temp)
          gui.update_ethIp(ip.get_ip_address("eth0"))
          if exit:
               break 
          gui.update_wanIp(ip.get_ip_address("wlan0"))
          if exit:
               break
          if battery.exist():
               bat_info=batt.get_baterry_info(battery)
               if exit:         
                   break
               gui.update_battery(bat_info['Percent'],bat_info['Current'])
          else:
               gui.update_battery(0,0)    
          if exit:
               break          
          tm.sleep(5)

#======== cansel thread sleep  ========
def cansel_threads():
    pass

#======== register display keys =======
def register_keys():
    try:
        from gpiozero import Button
    except:
        print('Fail register Keys')
        return
    global key1,key2,key3
    key1 = Button(18)
    key2 = Button(23)
    key3 = Button(24)
    key1.when_released = gui.key1_press
    key2.when_released = gui.key2_press
    key3.when_released = gui.key3_press


#======== Sreen Saver ========
def screensaver_disable(disable):
    try:        
        if disable:
            proc.run(["xset", "-dpms"])
            proc.run(["xset", "s","off"])
        else:
            proc.run(["xset", "+dpms"])
            proc.run(["xset", "s","on"])
    except:  
        return        

               
#======== Main =============== 
screensaver_disable(True)
gui = Gui()
# register Keys
#register_keys()
# start time thread
tm_thrd=thrd.Thread(target=time_thread)
tm_thrd.start()
# start lanIp thread
cpu_thrd=thrd.Thread(target=cpuInfo_thread)
cpu_thrd.start()
# start wheather thread
wether_thrd=thrd.Thread(target=weather_thread, args=(120,)) # sec update
wether_thrd.start()
# start sensor thread
sensor_thrd=thrd.Thread(target=sensor_thread, args=(60,)) # sec update
sensor_thrd.start()

gui.run()
cansel_threads()
tm_thrd.join()
cpu_thrd.join()
wether_thrd.join()
sensor_thrd.join()

screensaver_disable(False)
print("End...")
