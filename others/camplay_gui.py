import tkinter as tk
import Pmw as tk2
import time as tm
import threading as thrd
import sys, io

from picamera2_sim import Picamera2


APP_TITLE = "Cam Play"


##############################################################################################
#print a dictionary list
def pprint(obj, indent=0, pre='', out=sys.stdout):
    """Pretty-print a dictionary, list, or nested structure to the console."""
    space = ' ' * indent
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{space}{key}:", end=' ', file=out)
            if isinstance(value, (dict, list)):
                print("", file=out)
                pprint(value, indent + 2, pre, out)
            else:
                print(value, file=out)
    elif isinstance(obj, (list)):
        for i, item in enumerate(obj, start=1):
            print(f"{space}[{pre}{i}]", file=out)
            pprint(item, indent + 2, pre, out)
    else:
        print(space + str(obj), file=out)


##############################################################################################
class main_win:
    _TEXT_LABEL = "Available Cameras"
    _CAM_INF_PRE = "cam "    
    _cam_insts = [None,None,None,None]

    def __init__(self,cam_info):
        self.curr_caminfo = cam_info
        ####
        self.root = tk.Tk()
        tk2.initialise(self.root)
        self.root.title(APP_TITLE)
        self.root.geometry("400x200+20+50")
        #add buttons_frm ======
        frm2=tk.Frame(self.root)
        tk.Button(frm2, text="Update", command=self.__update_btn).pack(side=tk.LEFT, padx=5)
        tk.Button(frm2, text="Open", command=self.__open_btn).pack(side=tk.LEFT, padx=5)
        #add cam ListBox ------
        cbx_entries = self.__get_list_items(cam_info,self._CAM_INF_PRE)        
        self.cbx = tk2.ComboBox(frm2, label_text='Camera:', labelpos='w', listheight=60, dropdown=1, scrolledlist_items=cbx_entries)
        self.cbx.selectitem(cbx_entries[0])
        self.cbx.pack(side=tk.LEFT)
        frm2.pack(side=tk.BOTTOM, anchor=tk.W, pady=5)
        #add test frm ======        
        self.__add_ScrolledText_frame(cam_info)


    #draw text frame using tk.Text
    def __add_text_frame(self,view_obj):
        tk.Label(self.root, text=self._TEXT_LABEL).pack(side=tk.TOP)
        frm1=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)                
        self.text=tk.Text(frm1, height=30)
        scroll = tk.Scrollbar(frm1, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        #fill text info
        txtio = io.StringIO('')
        pprint(view_obj, pre=self._CAM_INF_PRE, out=txtio)
        self.text.insert(tk.END, txtio.getvalue())
        self.text.config(state=tk.DISABLED)
        #pack frm1
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.pack(side=tk.LEFT,fill=tk.BOTH)        
        frm1.pack(side=tk.TOP,fill=tk.BOTH, expand=1)


    #draw text frame using Pmw.ScrolledText
    def __add_ScrolledText_frame(self,view_obj):
        frm1=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)
        self.text = tk2.ScrolledText(frm1, borderframe=0, labelpos=tk.N, label_text=self._TEXT_LABEL, usehullsize=0,
            text_padx=5, text_pady=5, text_wrap='none')
        #fill text info
        txtio = io.StringIO('')
        pprint(view_obj, pre=self._CAM_INF_PRE, out=txtio)
        self.text.settext(txtio.getvalue())
        self.text.configure(text_state = 'disabled')
        #pack frm1                
        self.text.pack(fill=tk.BOTH, expand=1, padx=1, pady=1)
        frm1.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def __get_list_items(self,view_obj,pre):
        items = ()
        for i in range(len(view_obj)):
            item = pre+str(i+1)
            items = items + (item,)
        return items


    def __update_btn(self):        
        txtio = io.StringIO('')
        cam_info = Picamera2.global_camera_info()
        self.curr_caminfo = cam_info
        pprint(cam_info, pre=self._CAM_INF_PRE, out=txtio)
        #update Text
        if isinstance(self.text, tk2.ScrolledText):
            self.text.clear()
            self.text.settext(txtio.getvalue())
            self.text.configure(text_state = 'disabled')
        elif isinstance(self.text, tk.Text):
            self.text.config(state=tk.NORMAL)
            self.text.delete('1.0', tk.END)
            self.text.insert(tk.END, txtio.getvalue())
            self.text.config(state=tk.DISABLED)
        #update ComboBox
        cbx_entries = self.__get_list_items(cam_info,self._CAM_INF_PRE)
        self.cbx.setlist(cbx_entries)
        self.cbx.selectitem(cbx_entries[0])



    def __open_btn(self):        
        print('\nopen button:')
        cbxIdx = self.cbx.component('scrolledlist').curselection()[0]
        if cbxIdx > len(self._cam_insts) :
            print('Too many comeras')
            return
        print('Select idx:'+str(cbxIdx))
        cam_model =  self.curr_caminfo[cbxIdx]['Model']
        print('Select Model:'+cam_model)
        cam_num = self.curr_caminfo[cbxIdx]['Num']
        print('Select Cam Num:'+str(cam_num))
        if self._cam_insts[cbxIdx] != None:
            print(f'cam_insts {cbxIdx} aleary Open!')
            self._cam_insts[cbxIdx].on_top()
            return
        self._cam_insts[cbxIdx] = camera_win(cbxIdx, cam_model, cam_num)


    def run(self):
        self.root.mainloop()

##############################################################################################        
class camera_win:
    def __init__(self, idx, cam_model, cam_num):
        self.idx = idx
        self.cam_num = cam_num
        print(f'Open cam_insts {self.idx}')
        self.win = tk.Toplevel()
        self.win.title(cam_model)
        self.win.geometry("400x290+150+100")
        self.win.resizable(0,0)
        self.win.bind('<Destroy>',self.__close_win)
        #left butt form
        leftfrm = tk.Frame(self.win)
        tk.Button(leftfrm, text="Info", command=self.__info_btn, width=5).pack(side=tk.TOP, padx=2)
        tk.Button(leftfrm, text="Modes",  command=self.__modes_btn, width=5).pack(side=tk.TOP, padx=2)
        leftfrm.pack(side=tk.LEFT, fill=tk.Y, pady=4)
        #image form
        canvfrm = tk.Frame(self.win, relief=tk.GROOVE,  borderwidth=2)
        self.canvas = tk.Canvas(canvfrm, bg="lightgray", width=320, height=240)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        canvfrm.pack(side=tk.TOP, padx=4, pady=4)
        #bottom butt form
        botfrm = tk.Frame(self.win)
        tk.Button(botfrm, text="Foto").pack(side=tk.LEFT, padx=2)
        tk.Button(botfrm, text="Start Rec").pack(side=tk.LEFT, padx=2)
        botfrm.pack(side=tk.BOTTOM, fill=tk.X, pady=4)


    def __close_win(self,e):
        global mainWin
        print(f'Close cam_insts {self.idx}')
        mainWin._cam_insts[self.idx] = None

    def __info_btn(self):
        print(f"info butt [{self.cam_num}]")

    def __modes_btn(self):
        print(f"modes butt [{self.cam_num}]")

    def on_top(self):
        self.win.lift()


##############################################################################################
#test print cam infos
def test_print(camera_info):
    txtio = io.StringIO('')
    pprint(camera_info, pre=win._CAM_INF_PRE, out=txtio)
    print(txtio.getvalue(), end='')

#main function
if __name__ == '__main__':
    global mainWin
    print(APP_TITLE+" start...")   
    #get cameras info 
    camera_info = Picamera2.global_camera_info()
    #test_print(camera_info)
    #open Gui
    mainWin=main_win(camera_info)            
    #...
    mainWin.run()
    print("End")