import tkinter as tk
import Pmw as tk2

class options_win:

    def __init__(self, model, cam_prop,cam_modes):        
        self.win = tk.Toplevel()
        tk2.initialise(self.win)
        self.win.title("Options Model: "+model)
        self.win.geometry("400x300+200+150")
        #self.win.resizable(0,0)
        #add buttons_frm ======
        frm2=tk.Frame(self.win)
        tk.Button(frm2, text="Ok").pack(side=tk.LEFT, padx=5)
        tk.Button(frm2, text="Cancel").pack(side=tk.LEFT, padx=5)
        frm2.pack(side=tk.BOTTOM, anchor=tk.W, pady=3)        
        #add main_frm ======
        frm1=tk.Frame(self.win)
        nb = tk2.NoteBook(frm1)
        nb.add('Foto')
        nb.add('Video')
        nb.add('Stream')       
        nb.pack(padx=3, pady=3, fill=tk.BOTH, expand=1)      
        frm1.pack(side=tk.TOP,fill=tk.BOTH, expand=1)  
            