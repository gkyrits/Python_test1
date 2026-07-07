import tkinter as tk
import Pmw as tk2
import sys,io

import genutils as utl
import camwork as cam

INFO_FONT = "Arial 8"

##############################################################################################
#print a dictionary list
def d_print(obj, indent=0, pre='', out=sys.stdout):
    """Pretty-print a dictionary, list, or nested structure to the console."""
    space = ' ' * indent
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{space}{key}:", end=' ', file=out)
            if isinstance(value, (dict, list)):
                print("", file=out)
                d_print(value, indent + 2, pre, out)
            else:
                print(value, file=out)
    elif isinstance(obj, (list)):
        for i, item in enumerate(obj, start=1):
            print(f"{space}[{pre}{i}]", file=out)
            d_print(item, indent + 2, pre, out)
    else:
        print(space + str(obj), file=out)



##############################################################################################
# filename utils
##############################################################################################

def get_dtime_post():
    """Get a date-time string for filename postfix."""
    from datetime import datetime
    now = datetime.now()
    return now.strftime("_%Y%m%d_%H%M%S")

def get_filename(options, part):
    """Get a filename based on configured option."""
    path = options[part]['path']
    name = options[part]['name']
    ext = options[part]['format']
    #fix extension for video format
    if part == "video":
        encod = options[part]['encoder']
        if encod == "H264":
            ext = "h264"
        elif encod == "MJPEG":
            ext = "mjpeg"
        elif encod == "jpeg":
            ext = "jpeg"
        elif encod == "none":
            ext = "raw"
    dtime_post = options[part]['fname_dtime']
    if dtime_post:
        post = utl.get_dtime_post()
    else:
        post = ""
    if path and name and ext:
        return f"{path}/{name}{post}.{ext}"
    else:
        return "foto.jpg"

    


##############################################################################################
# Text Info Window Class
##############################################################################################
class info_win:

    def __init__(self, parent, model, info, id):
        self.parent = parent
        self.model = model
        self.id = id
        if id == cam.camera_win.INFO_PROP_ID:
            self.label = 'Properties'
        elif id == cam.camera_win.INFO_SENSOR_ID:
            self.label = 'Sensor Modes'
        self.win = tk.Toplevel()
        self.win.title(model+" "+self.label)
        self.win.geometry("350x200+200+150")
        self.win.bind('<Destroy>',self.__close_win)
        self.__add_ScrolledText_frame(info)


    def __add_ScrolledText_frame(self,view_obj):
        frm1=tk.Frame(self.win, relief=tk.GROOVE,  borderwidth=2)
        self.text = tk2.ScrolledText(frm1, borderframe=0, labelpos=tk.N, label_text=self.label, usehullsize=0,
            text_padx=2, text_pady=2, text_wrap='none', text_font =utl.INFO_FONT)
        #fill text info
        txtio = io.StringIO('')
        utl.d_print(view_obj, out=txtio)
        self.text.settext(txtio.getvalue())
        self.text.configure(text_state = 'disabled')
        #pack frm1
        self.text.pack(fill=tk.BOTH, expand=1, padx=1, pady=1)
        frm1.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def __close_win(self,e):
        print(f'Close Info [{self.model}]')
        if self.id == cam.camera_win.INFO_PROP_ID:
            self.parent.propInf_win = None
        elif self.id == cam.camera_win.INFO_SENSOR_ID:
            self.parent.sensorInf_win = None


    def destroy(self):
        self.win.destroy()


    def on_top(self):
        self.win.lift()        