import tkinter as tk
import Pmw as tk2
import io

import genutils as utl
import camwork as cam

global Picamera2

def import_special_libs():
    global Picamera2
    try:
        from picamera2 import Picamera2
    except Exception as e:
        print("Error importing : ", e.__str__())
        from picamera2_sim import Picamera2
        print('import simulation libs')



APP_TITLE = "Cam Play"

global mainWin
mainWin = None

##############################################################################################
# Available Window Class
##############################################################################################
class main_win:
    _TEXT_LABEL = "Available Cameras"
    _CAM_INF_PRE = "cam "
    cam_inst = [None,None,None,None]

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
        utl.d_print(view_obj, pre=self._CAM_INF_PRE, out=txtio)
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
            text_padx=2, text_pady=2, text_wrap='none',text_font =utl.INFO_FONT)
        #fill text info
        txtio = io.StringIO('')
        utl.d_print(view_obj, pre=self._CAM_INF_PRE, out=txtio)
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
        utl.d_print(cam_info, pre=self._CAM_INF_PRE, out=txtio)
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
        if cbxIdx > len(self.cam_inst) :
            print('Too many comeras')
            return
        print('Select idx:'+str(cbxIdx))
        cam_model =  self.curr_caminfo[cbxIdx]['Model']
        print('Select Model:'+cam_model)
        cam_num = self.curr_caminfo[cbxIdx]['Num']
        print('Select Cam Num:'+str(cam_num))
        if self.cam_inst[cbxIdx] != None:
            # Check if the window still exists
            if self.cam_inst[cbxIdx].win.winfo_exists():
                print(f'cam_inst {cbxIdx} aleary Open!')
                self.cam_inst[cbxIdx].on_top()
                return
            else:
                # Window was closed, clean up the reference
                self.cam_inst[cbxIdx] = None
        self.cam_inst[cbxIdx] = cam.camera_win(cbxIdx, cam_model, cam_num)


    def run(self):
        self.root.mainloop()



##############################################################################################
# Main
##############################################################################################
#test print cam infos
def test_print(camera_info):
    txtio = io.StringIO('')
    utl.d_print(camera_info, pre=main_win._CAM_INF_PRE, out=txtio)
    print(txtio.getvalue(), end='')

#main function
if __name__ == '__main__':
    import_special_libs()    
    print(APP_TITLE+" start...")
    #get cameras info
    camera_info = Picamera2.global_camera_info()
    #test_print(camera_info)
    #open Gui
    mainWin=main_win(camera_info)
    #...
    mainWin.run()
    print("End")
