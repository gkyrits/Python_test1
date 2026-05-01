import tkinter as tk
import threading as thrd
import socket



class main_win:
    APP_TITLE = "Camera Client"
    PORT = 8000

    def __init__(self):
        self.sock = None
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


    def client_thead(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.statusLbl.configure(text='Wait Connect')
        try:
            self.sock.connect((self.ipStr.get(),self.PORT))           
        except Exception as e:
            print(f'Error1: {e}')
            self.message_win(str(e))
            self.statusLbl.configure(text='Disconnected')
            self.sock = None
            print('client_thead Exit!')
            return
        self.statusLbl.configure(text="Connected")
        #...


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
                print(f'Error2: {e}')
                self.message_win(str(e))
                return
            print('wait thead..')
            self.client_thrd.join()
            self.sock = None
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

