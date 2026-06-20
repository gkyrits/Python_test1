import tkinter as tk
import Pmw as tk2

BOX_FONT = "Arial 8"

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
        p1=nb.add('Foto')
        p2=nb.add('Video')
        p3=nb.add('Stream')
        #--(foto)
        self.dir_path(p1)
        self.image_quality(p1)
        self.image_size(p1)
        self.image_format(p1)
        self.file_name(p1)
        #---(video)
        self.dir_path(p2)
        self.image_size(p2)
        #---(stream)
        self.image_size(p3)
        nb.pack(padx=3, pady=3, fill=tk.BOTH, expand=1)      
        frm1.pack(side=tk.TOP,fill=tk.BOTH, expand=1)  


    def dir_path(self,parent):
        path = tk.StringVar()
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm, text="Save Path").pack(side=tk.TOP, anchor=tk.W)
        tk.Entry(frm, textvariable=path, width=20).pack(side=tk.LEFT, fill=tk.X, expand=1, padx=2)
        tk.Button(frm, text="..", command=lambda: self.browse_dir(path)).pack(side=tk.RIGHT, padx=2)
        frm.pack(side=tk.TOP, anchor=tk.W, fill=tk.X)

    def browse_dir(self, path):
        from tkinter import filedialog
        seldir = filedialog.askdirectory(title="Select Directory")
        if seldir:
            path.set(seldir)


    def image_size(self,parent):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm, text="Image Size").pack(side=tk.TOP, anchor=tk.W)
        cbx_entries = ['160x120', '320x240', '640x480', "1280x960", "2560x1920"] 
        cbx = tk2.ComboBox(frm, labelpos='w', entry_width=10, listheight=80, dropdown=1, scrolledlist_items=cbx_entries) # label_text='Size:',
        cbx.selectitem(cbx_entries[1])
        cbx.pack(side=tk.LEFT, padx=2)
        frm.pack(side=tk.LEFT, anchor=tk.N)


    def image_format(self,parent):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm, text="Image Format").pack(side=tk.TOP, anchor=tk.W)
        cbx_entries = ['jpeg', 'png', 'bmp', "gif"] 
        cbx = tk2.ComboBox(frm, labelpos='w', entry_width=10, listheight=80, dropdown=1, scrolledlist_items=cbx_entries) # label_text='Size:',
        cbx.selectitem(cbx_entries[0])
        cbx.pack(side=tk.LEFT, padx=2)
        frm.pack(side=tk.LEFT, anchor=tk.N)


    def image_quality(self,parent):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        
        # JPEG Quality row
        tk.Label(frm, text="JPEG Quality :").grid(row=0, column=0, sticky=tk.W, padx=2)
        tk.Label(frm, text="0").grid(row=0, column=1, sticky=tk.W, padx=2)
        tk.Scale(frm, from_=0, to=95, orient=tk.HORIZONTAL, showvalue=0).grid(row=0, column=2, sticky=tk.EW, padx=2)
        
        # PNG Compression row
        tk.Label(frm, text="PNG Compression :").grid(row=1, column=0, sticky=tk.W, padx=2)
        tk.Label(frm, text="0").grid(row=1, column=1, sticky=tk.W, padx=2)
        tk.Scale(frm, from_=0, to=9, orient=tk.HORIZONTAL, showvalue=0).grid(row=1, column=2, sticky=tk.EW, padx=2)
        
        frm.columnconfigure(2, weight=1)
        frm.pack(side=tk.TOP, fill=tk.X, anchor=tk.W) 


    def file_name(self,parent):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm, text="File Name").pack(side=tk.TOP, anchor=tk.W)
        tk.Entry(frm, width=20).pack(side=tk.TOP, fill=tk.X, expand=1, padx=4)
        tk.Checkbutton(frm, text="Num").pack(side=tk.LEFT, padx=2)
        tk.Checkbutton(frm, text="Date").pack(side=tk.LEFT, padx=2)
        frm.pack(side=tk.TOP, anchor=tk.W, fill=tk.X)