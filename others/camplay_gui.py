import tkinter as tk
import Pmw as tk2
import time as tm
import PIL.Image as Image
import PIL.ImageTk as ImageTk
import threading as thrd
import sys, io

from picamera2 import Picamera2, Preview
from libcamera import Transform


APP_TITLE = "Cam Play"
INFO_FONT = "Arial 8"

_pil_view_exit = [False,False,False,False]


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
    cam_insts = [None,None,None,None]

    def __init__(self,cam_info):
        self.curr_caminfo = cam_info
        ####
        self.root = tk.Tk()
        tk2.initialise(self.root)
        self.root.title(APP_TITLE)
        self.root.geometry("350x200+20+50")
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
            text_padx=2, text_pady=2, text_wrap='none',text_font =INFO_FONT)
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
        if cbxIdx > len(self.cam_insts) :
            print('Too many comeras')
            return
        print('Select idx:'+str(cbxIdx))
        cam_model =  self.curr_caminfo[cbxIdx]['Model']
        print('Select Model:'+cam_model)
        cam_num = self.curr_caminfo[cbxIdx]['Num']
        print('Select Cam Num:'+str(cam_num))
        if self.cam_insts[cbxIdx] != None:
            print(f'cam_insts {cbxIdx} aleary Open!')
            self.cam_insts[cbxIdx].on_top()
            return
        self.cam_insts[cbxIdx] = camera_win(cbxIdx, cam_model, cam_num)


    def run(self):
        self.root.mainloop()

##############################################################################################
class camera_win:
    INFO_PROP_ID = 0
    INFO_SENSOR_ID = 1

    def __init__(self, idx, cam_model, cam_num):
        self.idx = idx
        self.cam_num = cam_num
        self.cam_model = cam_model
        self.picam = None
        self.propInf_win = None
        self.sensorInf_win = None
        self.preview_on = False
        self.view_pil_on = False
        self.pvimg = None
        self.hflip = tk.IntVar()
        self.vflip = tk.IntVar()
        print(f'Start camera win {self.idx}')
        #build window
        self.win = tk.Toplevel()
        self.win.title(cam_model)
        self.win.geometry("420x310+150+100")
        self.win.resizable(0,0)
        self.win.bind('<Destroy>',self.__close_win)
        #menu
        mnBar = tk.Frame(self.win, relief=tk.SUNKEN, borderwidth=1, height=20)
        mnBar.pack(fill=tk.X)
        mnBar.pack_propagate(False)
        mnBtn1 = tk.Menubutton(mnBar, text='Info', underline=0)
        mnBtn1.pack(side=tk.LEFT, padx="2m")
        mnBtn1.menu = tk.Menu(mnBtn1)
        mnBtn1.menu.add_command(label='Properties', underline=0, command=self.__info_btn)
        mnBtn1.menu.add_command(label='Sensor Modes', underline=0, command=self.__modes_btn)
        mnBtn1['menu'] = mnBtn1.menu
        #left butt form
        leftfrm = tk.Frame(self.win)
        tk.Button(leftfrm, text="Snap", command=self.__snap_pil_image, width=7).pack(side=tk.TOP, padx=2)
        tk.Button(leftfrm, text="View", command=self.__preview_pil_image, width=7).pack(side=tk.TOP, padx=2)
        tk.Button(leftfrm, text="PreView", command=self.__preview_btn, width=7).pack(side=tk.TOP, padx=2)
        #--frame checkbuttons
        ckbtnFrm = tk.Frame(leftfrm)
        tk.Checkbutton(ckbtnFrm, text="H rot", variable=self.hflip, onvalue=1, offvalue=0, command=self.__rotate_ckbox).pack(side=tk.TOP)
        tk.Checkbutton(ckbtnFrm, text="V rot", variable=self.vflip, onvalue=1, offvalue=0, command=self.__rotate_ckbox).pack(side=tk.TOP)
        ckbtnFrm.pack(side=tk.BOTTOM, anchor=tk.W)
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
        #initialize Camera
        self.__initialize_Camera()


    def __initialize_Camera(self):
        print(f'Open cam_insts {self.cam_num}')
        self.picam = Picamera2(self.cam_num)
        self.cam_modes = self.picam.sensor_modes
        #cam_prv_cfg = self.picam.create_preview_configuration(lores={"size": (320, 240)}, display="lores", encode="lores")
        self.cam_prv_cfg = self.picam.create_preview_configuration(main={"size": (320, 240)})
        print("--------")
        pprint(self.cam_prv_cfg)
        print("--------")
        self.picam.configure(self.cam_prv_cfg)
        self.picam.start()


    def __close_win(self,e):
        global mainWin
        if self.propInf_win != None:
            self.propInf_win.destroy()
        if self.sensorInf_win != None:
            self.sensorInf_win.destroy()
        if self.picam != None:
            self.picam.stop()
            self.picam = None
        print(f'Close cam_insts {self.cam_num}')
        mainWin.cam_insts[self.idx] = None


    def __info_btn(self):
        print(f"info butt [{self.cam_num}]")
        if self.propInf_win == None:
            self.propInf_win = info_win(self,self.cam_model,self.picam.camera_properties,self.INFO_PROP_ID)
        else:
            print(f"info [{self.cam_model}] already Open!")
            self.propInf_win.on_top()


    def __modes_btn(self):
        print(f"Modes butt [{self.cam_num}]")
        if self.sensorInf_win == None:
            self.sensorInf_win = info_win(self,self.cam_model,self.cam_modes,self.INFO_SENSOR_ID)
        else:
            print(f"Modes [{self.cam_model}] already Open!")
            self.sensorInf_win.on_top()


    def __rotate_ckbox(self):
        hflp = self.hflip.get()
        vflp = self.vflip.get()
        print('hflip='+str(hflp)+'  vflip='+str(vflp))
        self.picam.stop()
        self.cam_prv_cfg["transform"] = Transform(hflip=hflp, vflip=vflp)
        self.picam.configure(self.cam_prv_cfg)
        self.picam.start()
        if self.preview_on:
            self.picam.stop_preview()
            self.picam.start_preview(Preview.QT, width=320, height=240)



    def __preview_btn(self):
        if not self.preview_on:
            self.preview_on = True
            self.picam.stop_preview()
            self.picam.start_preview(Preview.QT, width=320, height=240)
        else:
            self.preview_on = False
            self.picam.stop_preview()
            self.picam.start_preview(Preview.NULL)


    def __snap_pil_image(self):
        print('snap PIL image ...')
        pilimg = self.picam.capture_image('main')
        self.tkimg = ImageTk.PhotoImage(pilimg)
        self.canvas.create_image(1,1,anchor=tk.NW,image=self.tkimg)
        self.canvas.update()


    def __preview_pil_image(self):
        if not self.view_pil_on:
            # start PIL thread
            print('preview PIL start ...')
            self.view_pil_on = True
            self.win.after(100,self.__pil_image_loop)
        else:
            self.view_pil_on = False


    def __pil_image_loop(self):
        pilimg = self.picam.capture_image('main')
        self.tkimg = ImageTk.PhotoImage(pilimg)
        if self.pvimg == None:
            self.pvimg = self.canvas.create_image(1,1,anchor=tk.NW,image=self.tkimg)
        else:
            self.canvas.itemconfig(self.pvimg, image=self.tkimg)
        if self.view_pil_on:
            self.win.after(100,self.__pil_image_loop)


    def on_top(self):
        self.win.lift()


    def close(self):
        self.win.destroy()


##############################################################################################
class info_win:

    def __init__(self, parent, model, info, id):
        self.parent = parent
        self.model = model
        self.id = id
        if id == camera_win.INFO_PROP_ID:
            self.label = 'Properties'
        elif id == camera_win.INFO_SENSOR_ID:
            self.label = 'Sensor Modes'
        self.win = tk.Toplevel()
        self.win.title(model+" "+self.label)
        self.win.geometry("350x200+200+150")
        self.win.bind('<Destroy>',self.__close_win)
        self.__add_ScrolledText_frame(info)


    def __add_ScrolledText_frame(self,view_obj):
        frm1=tk.Frame(self.win, relief=tk.GROOVE,  borderwidth=2)
        self.text = tk2.ScrolledText(frm1, borderframe=0, labelpos=tk.N, label_text=self.label, usehullsize=0,
            text_padx=2, text_pady=2, text_wrap='none', text_font =INFO_FONT)
        #fill text info
        txtio = io.StringIO('')
        pprint(view_obj, out=txtio)
        self.text.settext(txtio.getvalue())
        self.text.configure(text_state = 'disabled')
        #pack frm1
        self.text.pack(fill=tk.BOTH, expand=1, padx=1, pady=1)
        frm1.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def __close_win(self,e):
        print(f'Close Info [{self.model}]')
        if self.id == camera_win.INFO_PROP_ID:
            self.parent.propInf_win = None
        elif self.id == camera_win.INFO_SENSOR_ID:
            self.parent.sensorInf_win = None


    def destroy(self):
        self.win.destroy()


    def on_top(self):
        self.win.lift()



##############################################################################################
#test print cam infos
def test_print(camera_info):
    txtio = io.StringIO('')
    pprint(camera_info, pre=main_win._CAM_INF_PRE, out=txtio)
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
