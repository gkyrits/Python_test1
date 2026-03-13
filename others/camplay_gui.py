import tkinter as tk
import Pmw as tk2
import time as tm
import threading as thrd
import sys, io

from picamera2_sim import Picamera2


APP_TITLE = "Cam Play"

##############################################################################################
#print a dictionary list
def pprint(obj, indent=0, out=sys.stdout):
    """Pretty-print a dictionary, list, or nested structure to the console."""
    space = ' ' * indent
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{space}{key}:", end=' ', file=out)
            if isinstance(value, (dict, list)):
                print("", file=out)
                pprint(value, indent + 2, out)
            else:
                print(value, file=out)
    elif isinstance(obj, (list)):
        for i, item in enumerate(obj, start=1):
            print(f"{space}[{i}]", file=out)
            pprint(item, indent + 2, out)
    else:
        print(space + str(obj), file=out)


##############################################################################################
class main_win:

    def __init__(self,caminfo_obj):
        self.root = tk.Tk()
        tk2.initialise(self.root)
        self.root.title(APP_TITLE)
        self.root.geometry("400x200+20+50")
        #add buttons_frm ======
        frm2=tk.Frame(self.root)
        tk.Button(frm2, text="Update", command=self.__update_btn).pack(side=tk.LEFT, padx=5)
        tk.Button(frm2, text="Open", command=self.__open_btn).pack(side=tk.LEFT, padx=5)
        #add cam ListBox ------
        cbx_entries = ('cam 1','cam 2','cam 3')
        cbx = tk2.ComboBox(frm2, label_text='Cam:', labelpos='w', listheight=60, dropdown=1, scrolledlist_items=cbx_entries)
        cbx.selectitem(cbx_entries[0])
        cbx.pack(side=tk.LEFT)
        frm2.pack(side=tk.BOTTOM, anchor=tk.W, pady=5)
        #add test frm ======
        self._TEXT_LABEL = "Available Cameras"
        self.__add_ScrolledText_frame(caminfo_obj)


    #draw text frame using tk.Text
    def __add_text_frame(self,view_obj):
        tk.Label(self.root, text=self._TEXT_LABEL).pack(side=tk.TOP)
        frm1=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)                
        self.text=tk.Text(frm1, height=30)
        scroll = tk.Scrollbar(frm1, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        #fill text info
        txtio = io.StringIO('')
        pprint(view_obj, out=txtio)
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
        pprint(view_obj, out=txtio)
        self.text.settext(txtio.getvalue())
        self.text.configure(text_state = 'disabled')
        #pack frm1                
        self.text.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)
        frm1.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def __update_btn(self):
        print('update button')        
        txtio = io.StringIO('')
        info = Picamera2._cam1_sens_obj
        pprint(info, out=txtio)
        if isinstance(self.text, tk2.ScrolledText):
            self.text.clear()
            self.text.settext(txtio.getvalue())
            self.text.configure(text_state = 'disabled')
        elif isinstance(self.text, tk.Text):
            self.text.config(state=tk.NORMAL)
            self.text.delete('1.0', tk.END)
            self.text.insert(tk.END, txtio.getvalue())
            self.text.config(state=tk.DISABLED)



    def __open_btn(self):
        print('open button')        


    def run(self):
        self.root.mainloop() 

##############################################################################################
#main function
if __name__ == '__main__':
    print(APP_TITLE+" start...")
    camera_info = Picamera2.global_camera_info()
    #test pprint camera_info
    txtio = io.StringIO('')
    pprint(camera_info, out=txtio)
    print(txtio.getvalue(), end='')
    #open Gui
    win=main_win(camera_info)
    #...
    win.run()
    print("End")