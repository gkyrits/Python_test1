import tkinter as tk
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import threading as thrd
import time as tm
import camutils as utl
import socket
    
    
class main_win:
    APP_TITLE = "Camera Client"
    PORT = 8000

    def __init__(self):
        self.sock = None
        self.tkimg = None
        self.pilimg = None  # Keep PIL image reference
        self.pvimg = None
        self.last_update_time = 0
        self.min_update_interval = 0.033  # fps throttle (0.033=30fps) (0.05=20fps) (0.016=60fps)
        self.update_pending = False  # Prevent multiple updates queued
        self.root = tk.Tk()
        self.root.title(self.APP_TITLE)
        self.root.minsize(250, 150)
        self.root.grid_rowconfigure(0, weight=1) #resize grid
        self.root.grid_columnconfigure(0, weight=1) #resize grid
        #self.root.geometry("350x200+20+50")
        #image form
        canvfrm = tk.Frame(self.root, relief=tk.GROOVE, borderwidth=2)
        self.canvas = tk.Canvas(canvfrm, bg="lightgray",  width=320, height=240)
        self.canvas.bind("<Configure>", self.canvas_resize)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        canvfrm.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        #option form
        self.ipStr = tk.StringVar(value='0.0.0.0')
        optfrm = tk.Frame(self.root)
        ipfrm = tk.Frame(optfrm)
        tk.Label(ipfrm, text='IP: ').pack(side=tk.LEFT)
        tk.Entry(ipfrm, width=20, textvariable=self.ipStr).pack(side=tk.LEFT)
        ipfrm.pack(side=tk.TOP, anchor=tk.W, padx=2, pady=2)
        btnfrm = tk.Frame(optfrm)
        tk.Button(btnfrm, text='Connect', command=self.connect_btn).pack(side=tk.LEFT)
        btnfrm.pack(side=tk.TOP, anchor=tk.W, padx=2, pady=2)
        statusfrm = tk.Frame(optfrm, relief=tk.SUNKEN, borderwidth=1)
        self.statusLbl = tk.Label(statusfrm,text='Disconnected')
        self.statusLbl.pack(side=tk.LEFT)
        tk.Label(statusfrm,text=' Canvas:').pack(side=tk.LEFT)
        self.canvSizeLbl = tk.Label(statusfrm,text='100x100')
        self.canvSizeLbl.pack(side=tk.LEFT)        
        statusfrm.pack(side=tk.BOTTOM, fill=tk.X, expand=tk.YES, padx=1, pady=1)
        optfrm.grid(row=1, column=0, sticky="ew")


    def canvas_resize(self,event):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvSizeLbl.configure(text=str(width)+'x'+str(height))


    def message_win(self,msg):
        print(self.root.winfo_x(), self.root.winfo_y())
        win = tk.Toplevel()
        win.title('Exception')
        pos = '200x150+'+str(self.root.winfo_x()+50)+'+'+str(self.root.winfo_y()+50)
        win.geometry(pos)
        tk.Message(win,text=msg, justify='left', width=200, relief=tk.GROOVE).pack(fill=tk.BOTH, expand=tk.YES, padx=2, pady=2)


    def draw_image(self):
        #print('Draw Image...')
        self.update_pending = False
        if self.pvimg == None and self.tkimg is not None:
            self.pvimg = self.canvas.create_image(1, 1, anchor=tk.NW, image=self.tkimg)
        elif self.tkimg is not None:
            self.canvas.itemconfig(self.pvimg, image=self.tkimg)


    def client_loop(self):
        camcfg = None
        while True:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            reqInfo1 = {'Cmd': utl.CMG_IMG_CFG_REQ, 'Size': (width, height)}
            reqInfo2 = {'Cmd': utl.CMG_IMG_BUF_REQ}
            if  self.sock == None:
                return
            try:
                #send CMG_IMG_CFG_REQ
                utl.send_dict(self.sock, reqInfo1)
                #print('sent dict:', reqInfo1)
                #wait receive
                ackInfo = utl.recv_dict(self.sock)
                if ackInfo==None:
                    return
                #print('received dict:', ackInfo)
                if ackInfo['Cmd'] == utl.CMD_IMG_CFG_ACK:
                    camcfg = ackInfo['Config']
                #send CMG_IMG_BUF_REQ    
                utl.send_dict(self.sock, reqInfo2)
                #print('sent dict:', reqInfo2)
                #wait receive
                ackInfo = utl.recv_dict(self.sock)
                if ackInfo==None:
                    return                                   
            except Exception as e:
                print(f'Error1: {e}')
                self.message_win(str(e))
                return
            #receive CMD_IMG_BUF_ACK    
            if ackInfo['Cmd'] == utl.CMD_IMG_BUF_ACK:
                buffer =  ackInfo['Buffer']
            if camcfg != None:
                current_time = tm.time()
                if current_time - self.last_update_time >= self.min_update_interval and not self.update_pending:
                    self.pilimg = utl.make_pil_image(buffer, camcfg)
                    self.tkimg = ImageTk.PhotoImage(self.pilimg)
                    self.update_pending = True
                    self.root.after(0, self.draw_image)
                    self.last_update_time = current_time



    def client_thead(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.statusLbl.configure(text='Wait Connect')
        try:
            self.sock.connect((self.ipStr.get(),self.PORT))           
        except Exception as e:
            print(f'Error2: {e}')
            self.message_win(str(e))
            self.statusLbl.configure(text='Disconnected')
            self.sock = None
            print('client_thead Exit!')
            return
        self.statusLbl.configure(text="Connected")
        self.client_loop()
        self.statusLbl.configure(text='Disconnected')
        self.sock = None
        print('client_thead Exit!')        


    def connect_btn(self):
        print('IP='+self.ipStr.get())
        if self.sock == None:
            self.client_thrd=thrd.Thread(target=self.client_thead)
            self.client_thrd.start()
        else:            
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
                self.sock.close()
            except Exception as e:
                print(f'Error3: {e}')
                self.message_win(str(e))
                return
            self.sock = None
            #print('wait thead..')
            #self.client_thrd.join()
            print('Closed!')


    def run(self):
        self.root.mainloop()


#main function
if __name__ == '__main__':
    #open Gui
    mainWin=main_win()
    #...
    mainWin.run()
    print("End")    

