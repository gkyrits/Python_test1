import tkinter as tk
import Pmw as tk2

class options_win:
    def __init__(self, model, cam_prop,cam_modes):        
        self.win = tk.Toplevel()
        self.win.title("Options Model: "+model)
        self.win.geometry("300x200+200+150")
        #self.win.resizable(0,0)

