import tkinter as tk
import Pmw as tk2

#BOX_FONT = "Arial 8"

cam_options = {
    "foto": {
        "path": "",
        "size": (2560, 1920),
        "format": "jpeg",
        "quality": 75,
        "compression": 3,
        "name": "foto",
        "fname_dtime": True,
        "fname_incnum": False
    },
    "video": {
        "path": "",
        "size": (1280, 960),
        "format": "mp4",
        "quality": "medium",
        "encoder": "auto",
        "duration": 10,
        "audio_sync": 2.0,
        "name": "video",
        "fname_dtime": True,
        "fname_incnum": False
    },
    "stream": {
        "size": (640, 480)
    }
}

option_file = "cam_options.json"

class options_win:    

    def __init__(self, model, cam_prop,cam_modes):
        #foto variables
        self.qual_lbl = None
        self.compr_lbl = None        
        self.foto_path = tk.StringVar()
        self.foto_qual = tk.IntVar(value=75)
        self.foto_compr = tk.IntVar(value=3)        
        self.foto_size = (2560,1920)
        self.foto_format = "jpeg"
        self.foto_name = tk.StringVar(value="foto")
        self.foto_fname_dtime = tk.BooleanVar(value=True)
        self.foto_fname_incnum = tk.BooleanVar(value=False)
        #video variables
        self.video_path = tk.StringVar()
        self.video_size = (1280,960)
        self.video_format = "mp4"
        self.video_quality = "medium"
        self.video_encoder = "auto"
        self.video_duration = tk.IntVar(value=10)
        self.video_name = tk.StringVar(value="video")
        self.video_fname_dtime = tk.BooleanVar(value=True)
        self.video_fname_incnum = tk.BooleanVar(value=False)
        self.video_audio_sync = tk.DoubleVar(value=2.0)
        #sream variables
        self.stream_size = (640,480)
        #load options from file
        self._load_options()
        #create new window
        self.win = tk.Toplevel()
        tk2.initialise(self.win)
        self.win.title("Options Model: "+model)
        self.win.geometry("400x300+200+150")
        #self.win.resizable(0,0)
        #add buttons_frm ======
        frm2=tk.Frame(self.win)
        tk.Button(frm2, text="Ok", command=self._save_options).pack(side=tk.LEFT, padx=5)
        tk.Button(frm2, text="Cancel", command=self.win.destroy).pack(side=tk.LEFT, padx=5)
        frm2.pack(side=tk.BOTTOM, anchor=tk.W, pady=3)        
        #add main_frm ======
        frm1=tk.Frame(self.win)
        nb = tk2.NoteBook(frm1)
        p1=nb.add('Foto')
        p2=nb.add('Video')
        p3=nb.add('Stream')
        #--(foto)
        self.dir_path(p1,self.foto_path)
        self.file_name(p1,self.foto_name,self.foto_fname_dtime,self.foto_fname_incnum)
        self.image_quality_fnc(p1)
        self.foto_options(p1,"foto_size")
        #---(video)
        self.dir_path(p2,self.video_path)
        self.file_name(p2,self.video_name,self.video_fname_dtime,self.video_fname_incnum)
        self.video_encoder_options(p2)
        self.video_options(p2,"video_size")
        #---(stream)        
        self.image_size(p3,"stream_size")
        nb.pack(padx=3, pady=3, fill=tk.BOTH, expand=1)      
        frm1.pack(side=tk.TOP,fill=tk.BOTH, expand=1)  


    def dir_path(self,parent,path_var):        
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm, text="Save Path").pack(side=tk.TOP, anchor=tk.W)
        tk.Entry(frm, textvariable=path_var, width=20).pack(side=tk.LEFT, fill=tk.X, expand=1, padx=2)
        tk.Button(frm, text="..", command=lambda: self._browse_dir(path_var)).pack(side=tk.RIGHT, padx=2)
        frm.pack(side=tk.TOP, anchor=tk.W, fill=tk.X)

    def _browse_dir(self, path_var):
        from tkinter import filedialog
        seldir = filedialog.askdirectory(title="Select Directory")
        if seldir:
            path_var.set(seldir)


    def image_size(self,parent, size_attr):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm, text="Image Size").pack(side=tk.TOP, anchor=tk.W)
        cbx_entries = ['160x120', '320x240', '640x480', "1280x960", "2560x1920"] 
        cur_size = getattr(self, size_attr)
        cbx = tk2.ComboBox(frm, labelpos='w', entryfield_entry_width=10, listheight=80, dropdown=1, scrolledlist_items=cbx_entries, 
                           selectioncommand=lambda size: self._update_size(size, size_attr))
        #cbx.selectitem(cbx_entries[1])
        cbx.selectitem(f"{cur_size[0]}x{cur_size[1]}")
        cbx.pack(side=tk.LEFT, padx=2)
        frm.pack(side=tk.LEFT, anchor=tk.NW)

    def _update_size(self, size, size_attr):
        width, height = map(int, size.split('x'))
        setattr(self, size_attr, (width, height))


    def image_format_fnc(self,parent):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm, text="Image Format").pack(side=tk.TOP, anchor=tk.W)
        cbx_entries = ['jpeg', 'png', 'bmp', "gif"] 
        cbx = tk2.ComboBox(frm, labelpos='w', entryfield_entry_width=10, listheight=80, dropdown=1, scrolledlist_items=cbx_entries, selectioncommand=self._update_foto_format)
        cbx.selectitem(self.foto_format)
        cbx.pack(side=tk.LEFT, padx=2)
        frm.pack(side=tk.LEFT, anchor=tk.W)

    def _update_foto_format(self, fmt):
        self.foto_format = fmt


    def foto_options(self,parent, size_attr):    
        frm=tk.Frame(parent)
        self.image_size(frm,size_attr)
        self.image_format_fnc(frm)
        frm.pack(side=tk.TOP,  anchor=tk.W)


    def _slider_change(self, var):
        self.qual_lbl.config(text=str(self.foto_qual.get()))
        self.compr_lbl.config(text=str(self.foto_compr.get()))

    def image_quality_fnc(self,parent):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)        
        # JPEG Quality row        
        tk.Label(frm, text="JPEG Quality :").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.qual_lbl = tk.Label(frm, text=str(self.foto_qual.get()))
        self.qual_lbl.grid(row=0, column=1, sticky=tk.W, padx=2)
        tk.Scale(frm, from_=0, to=95, orient=tk.HORIZONTAL, showvalue=0, variable=self.foto_qual, command=self._slider_change).grid(row=0, column=2, sticky=tk.EW, padx=2)
        # PNG Compression row        
        tk.Label(frm, text="PNG Compression :").grid(row=1, column=0, sticky=tk.W, padx=2)
        self.compr_lbl = tk.Label(frm, text=str(self.foto_compr.get()))
        self.compr_lbl.grid(row=1, column=1, sticky=tk.W, padx=2)
        tk.Scale(frm, from_=0, to=9, orient=tk.HORIZONTAL, showvalue=0, variable=self.foto_compr, command=self._slider_change).grid(row=1, column=2, sticky=tk.EW, padx=2)
        frm.columnconfigure(2, weight=1)
        frm.pack(side=tk.TOP, fill=tk.X, anchor=tk.W) 


    def video_format_fnc(self,parent):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm, text="Video Format").pack(side=tk.TOP, anchor=tk.W)
        cbx_entries = ['mp4', 'avi', 'mov', 'mkv', "h264", "mjpg", "mjpeg"]
        cbx = tk2.ComboBox(frm, labelpos='w', entryfield_entry_width=10, listheight=80, dropdown=1, scrolledlist_items=cbx_entries, selectioncommand=self._update_video_format)
        cbx.selectitem(self.video_format)
        cbx.pack(side=tk.LEFT, padx=2)
        frm.pack(side=tk.LEFT, anchor=tk.W)

    def _update_video_format(self, fmt):
        self.video_format = fmt

    def video_quality_fnc(self,parent):
        #frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        frm=tk.Frame(parent)
        tk.Label(frm, text="Video Quality").pack(side=tk.TOP, anchor=tk.W)
        cbx_entries = ['very low','low', 'medium', 'high', 'very high']
        cbx = tk2.ComboBox(frm, labelpos='w', entryfield_entry_width=10, listheight=80, dropdown=1, scrolledlist_items=cbx_entries, selectioncommand=self._update_video_quality)
        cbx.selectitem(self.video_quality)
        cbx.pack(side=tk.LEFT, padx=2)
        frm.pack(side=tk.LEFT, anchor=tk.W)

    def _update_video_quality(self, quality):
        self.video_quality = quality


    def video_options(self,parent, size_attr):    
        frm=tk.Frame(parent)
        self.image_size(frm,size_attr)
        self.video_format_fnc(frm)
        self.audio_options(frm)
        frm.pack(side=tk.TOP,  anchor=tk.W)


    def video_encoder_fnc(self,parent):
        #frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        frm=tk.Frame(parent)
        tk.Label(frm, text="Video Encoder").pack(side=tk.TOP, anchor=tk.W)
        cbx_entries = ['auto','FFMPEG', 'H264', 'MJPEG', 'jpeg', 'none']
        cbx = tk2.ComboBox(frm, labelpos='w', entryfield_entry_width=10, listheight=80, dropdown=1, scrolledlist_items=cbx_entries, selectioncommand=self._update_video_encoder)
        cbx.selectitem(self.video_encoder)
        cbx.pack(side=tk.LEFT, padx=2)
        frm.pack(side=tk.LEFT, anchor=tk.W)

    def _update_video_encoder(self, encoder):
        self.video_encoder = encoder


    def video_encoder_options(self,parent):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)  
        self.video_encoder_fnc(frm)
        self.video_quality_fnc(frm)
        #..duration
        frmnm=tk.Frame(frm)
        tk.Label(frmnm, text="Duration").pack(side=tk.TOP, anchor=tk.W)
        tk.Entry(frmnm, width=5, textvariable=self.video_duration).pack(side=tk.LEFT, anchor=tk.W, padx=4)
        tk.Label(frmnm, text="Sec").pack(side=tk.LEFT, anchor=tk.W)
        frmnm.pack(side=tk.LEFT, anchor=tk.W)   
        #...     
        frm.pack(side=tk.TOP, fill=tk.X, anchor=tk.W)


    def audio_options(self,parent):
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)  
        tk.Label(frm, text="Audio Sync").pack(side=tk.TOP, anchor=tk.W)
        tk.Entry(frm, width=5, textvariable=self.video_audio_sync).pack(side=tk.LEFT, anchor=tk.W, padx=4)
        tk.Label(frm, text="Sec").pack(side=tk.LEFT, anchor=tk.W)
        frm.pack(side=tk.LEFT, fill=tk.X, anchor=tk.W)        


    #---file name frame
    def file_name(self,parent,fname,fname_dtime,fname_incnum):        
        frm=tk.Frame(parent, relief=tk.GROOVE,  borderwidth=2)
        frmnm=tk.Frame(frm)
        tk.Label(frmnm, text="File Name").pack(side=tk.TOP, anchor=tk.W)
        tk.Entry(frmnm, width=20, textvariable=fname).pack(side=tk.LEFT, anchor=tk.W, padx=4)
        frmnm.pack(side=tk.LEFT, anchor=tk.W)
        frmopt = tk.Frame(frm)
        auto_num_chk = tk.Checkbutton(frmopt, text="Auto Number", variable=fname_incnum, pady=0)
        auto_num_chk.pack(side=tk.TOP, anchor=tk.W, padx=2)
        date_chk = tk.Checkbutton(frmopt, text="DateTime", variable=fname_dtime, pady=0)
        date_chk.pack(side=tk.TOP, anchor=tk.W, padx=2)
        if fname_incnum.get():
            auto_num_chk.select()
        else:
            auto_num_chk.deselect()
        if fname_dtime.get():
            date_chk.select()
        else:
            date_chk.deselect()
        frmopt.pack(side=tk.LEFT, anchor=tk.W)        
        frm.pack(side=tk.TOP, anchor=tk.W, fill=tk.X) 

    #================================================

    def _load_options(self):
        #load options from file
        import json
        try:
            with open(option_file, 'r') as f:
                options = json.load(f)
            #foto options
            self.foto_path.set(options["foto"]["path"])
            self.foto_size = tuple(options["foto"]["size"])
            self.foto_format = options["foto"]["format"]
            self.foto_qual.set(options["foto"]["quality"])
            self.foto_compr.set(options["foto"]["compression"])
            self.foto_name.set(options["foto"]["name"])
            self.foto_fname_dtime.set(options["foto"]["fname_dtime"])
            self.foto_fname_incnum.set(options["foto"]["fname_incnum"])
            #video options
            self.video_path.set(options["video"]["path"])
            self.video_size = tuple(options["video"]["size"])
            self.video_name.set(options["video"]["name"])
            self.video_fname_dtime.set(options["video"]["fname_dtime"])
            self.video_fname_incnum.set(options["video"]["fname_incnum"])
            self.video_format = options["video"]["format"]
            self.video_quality = options["video"]["quality"]
            self.video_encoder = options["video"]["encoder"]
            self.video_duration.set(options["video"]["duration"])
            self.video_audio_sync.set(options["video"]["audio_sync"])
            #stream options
            self.stream_size = tuple(options["stream"]["size"])
        except FileNotFoundError:
            print(f"Options file {option_file} not found. Using default options.")


    def _save_options(self):
        #save options to file
        options = {
            "foto": {
                "path": self.foto_path.get(),
                "size": self.foto_size,
                "format": self.foto_format,
                "quality": self.foto_qual.get(),
                "compression": self.foto_compr.get(),
                "name": self.foto_name.get(),
                "fname_dtime": self.foto_fname_dtime.get(),
                "fname_incnum": self.foto_fname_incnum.get()
            },
            "video": {
                "path": self.video_path.get(),
                "size": self.video_size,
                "name": self.video_name.get(),
                "fname_dtime": self.video_fname_dtime.get(),
                "fname_incnum": self.video_fname_incnum.get(),
                "format": self.video_format,
                "quality": self.video_quality,
                "encoder": self.video_encoder,
                "duration": self.video_duration.get(),
                "audio_sync": self.video_audio_sync.get()
            },
            "stream": {
                "size": self.stream_size
            }
        }
        import json
        with open(option_file, 'w') as f:
            json.dump(options, f, indent=4)
        print(f"Options saved to {option_file}")
        #close window
        self.win.destroy()

############################################

def update_options():
    #update options from file
    import json
    try:
        with open(option_file, 'r') as f:
            options = json.load(f)
        #foto options
        cam_options["foto"]["path"] = options["foto"]["path"]
        cam_options["foto"]["size"] = tuple(options["foto"]["size"])
        cam_options["foto"]["format"] = options["foto"]["format"]
        cam_options["foto"]["quality"] = options["foto"]["quality"]
        cam_options["foto"]["compression"] = options["foto"]["compression"]
        cam_options["foto"]["name"] = options["foto"]["name"]
        cam_options["foto"]["fname_dtime"] = options["foto"]["fname_dtime"]
        cam_options["foto"]["fname_incnum"] = options["foto"]["fname_incnum"]
        #video options
        cam_options["video"]["path"] = options["video"]["path"]
        cam_options["video"]["size"] = tuple(options["video"]["size"])
        cam_options["video"]["name"] = options["video"]["name"]
        cam_options["video"]["fname_dtime"] = options["video"]["fname_dtime"]
        cam_options["video"]["fname_incnum"] = options["video"]["fname_incnum"]
        cam_options["video"]["format"] = options["video"]["format"]
        cam_options["video"]["quality"] = options["video"]["quality"]
        cam_options["video"]["encoder"] = options["video"]["encoder"]
        cam_options["video"]["duration"] = options["video"]["duration"]
        cam_options["video"]["audio_sync"] = options["video"]["audio_sync"]
        #stream options
        cam_options["stream"]["size"] = tuple(options["stream"]["size"])
    except FileNotFoundError:
        print(f"Options file {option_file} not found. Using default options.")
    except Exception as e:
        print(f"Error loading options: {e}. Using default options.")
        