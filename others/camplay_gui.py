import tkinter as tk
import Pmw as tk2
import time as tm
import threading as thrd
import sys
import io

APP_TITLE = "Cam Play"

cameras_obj  = [{'Model': 'ov5647', 'Location': 2, 'Rotation': 0, 'Id': '/base/soc/i2c0mux/i2c@1/ov5647@36', 'Num': 0}, {'Model': 'UVC Camera (046d:0825)', 'Location': 0, 'Id': '/base/soc/usb@7e980000/usb1@1-1.5:1.0-046d:0825', 'Num': 2}, {'Model': 'USB2.0 PC CAMERA', 'Location': 0, 'Id': '/base/soc/usb@7e980000/usb1@1-1.4:1.0-18ec:3299', 'Num': 1}]

cam1_prop_obj = {'Model': 'ov5647', 'UnitCellSize': (1400, 1400), 'Location': 2, 'Rotation': 0, 'PixelArraySize': (2592, 1944), 'ColorFilterArrangement': 2, 'PixelArrayActiveAreas': [(16, 6, 2592, 1944)], 'ScalerCropMaximum': (0, 0, 0, 0), 'SystemDevices': (20749, 20737, 20738, 20739)}
cam1_sens_obj = [{'format': 'SGBRG10_CSI2P', 'unpacked': 'SGBRG10', 'bit_depth': 10, 'size': (640, 480), 'fps': 58.92, 'crop_limits': (16, 0, 2560, 1920), 'exposure_limits': (134, 4879289, 20000)}, {'format': 'SGBRG10_CSI2P', 'unpacked': 'SGBRG10', 'bit_depth': 10, 'size': (1296, 972), 'fps': 46.34, 'crop_limits': (0, 0, 2592, 1944), 'exposure_limits': (86, 3066985, 20000)}, {'format': 'SGBRG10_CSI2P', 'unpacked': 'SGBRG10', 'bit_depth': 10, 'size': (1920, 1080), 'fps': 32.81, 'crop_limits': (348, 434, 1928, 1080), 'exposure_limits': (110, 3066979, 20000)}, {'format': 'SGBRG10_CSI2P', 'unpacked': 'SGBRG10', 'bit_depth': 10, 'size': (2592, 1944), 'fps': 15.63, 'crop_limits': (0, 0, 2592, 1944), 'exposure_limits': (130, 3066985, 20000)}]

cam2_prop_obj = {'Model': 'UVC Camera (046d:0825)', 'Location': 0, 'PixelArraySize': (1280, 960), 'PixelArrayActiveAreas': [(0, 0, 1280, 960)], 'SystemDevices': (20753,)}
com2_sens_obj = [{'format': 'MJPEG'}, {'format': 'YUYV'}] 

cam3_prop_obj = {'Model': 'USB2.0 PC CAMERA', 'Location': 0, 'PixelArraySize': (640, 480), 'PixelArrayActiveAreas': [(0, 0, 640, 480)], 'SystemDevices': (20751,)}
cam3_sens_obs = [{'format': 'YUYV'}]

#print a dictionary list
def pprint(obj, indent=0, out=sys.stdout):
    """Pretty-print a dictionary, list, or nested structure to the console."""
    space = ' ' * indent
    if isinstance(obj, dict):
        for key, value in obj.items():
            print(f"{space}{key}:", end=' ', file=out)
            if isinstance(value, (dict, list, tuple)):
                print("", file=out)
                pprint(value, indent + 2, out)
            else:
                print(value, file=out)
    elif isinstance(obj, (list, tuple)):
        for i, item in enumerate(obj, start=1):
            print(f"{space}[{i}]", file=out)
            pprint(item, indent + 2, out)
    else:
        print(space + str(obj), file=out)



class main_win:
    def __init__(self,title):
        self.root = tk.Tk()
        tk2.initialise(self.root)
        self.root.title(title)
        self.root.geometry("400x200+20+50")
        #add buttons_frm ======
        frm2=tk.Frame(self.root)
        tk.Button(frm2, text="Update").pack(side=tk.LEFT, padx=5)
        tk.Button(frm2, text="Open").pack(side=tk.LEFT, padx=5)
        #add cam ListBox ------
        cbx_entries = ('cam 1','cam 2','cam 3')
        cbx = tk2.ComboBox(frm2, label_text='Cam:', labelpos='w', listheight=60, dropdown=1, scrolledlist_items=cbx_entries)
        cbx.selectitem(cbx_entries[0])
        cbx.pack(side=tk.LEFT)
        frm2.pack(side=tk.BOTTOM, anchor=tk.W, pady=5)
        #add text_frm ======
        tk.Label(self.root, text="Available Cameras").pack(side=tk.TOP)
        frm1=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)                
        text=tk.Text(frm1, height=30)
        scroll = tk.Scrollbar(frm1, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        #fill text info
        txtio = io.StringIO('')
        pprint(cameras_obj, out=txtio)
        text.insert(tk.END, txtio.getvalue())
        text.config(state=tk.DISABLED)
        #pack frm1
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT,fill=tk.BOTH)        
        frm1.pack(side=tk.TOP,fill=tk.X)



    def run(self):
        self.root.mainloop() 


#main function
if __name__ == '__main__':
    print(APP_TITLE+" start...")    
    txtio = io.StringIO('')
    pprint(cam1_sens_obj, out=txtio)
    print(txtio.getvalue(), end='')
    win=main_win(APP_TITLE+" V0.1")
    #...
    win.run()
    print("End")