
import os
import tkinter as tk
from tkinter import Image, ttk
from tkinter import filedialog
from tkinter import messagebox
import PIL.Image as Image
import PIL.ImageTk as ImageTk


class server_win:
    APP_TITLE = "Test Server"
    PORT = 8000
    IP = '127.0.0.1'
    OPT_FILE = "server.opt"

    def __init__(self):
        self.path_files = []
        self.file_idx = 0
        #initialize Form
        self.root = tk.Tk()        
        self.portStr = tk.StringVar(value=str(self.PORT))
        self.pathStr = tk.StringVar(value="No path")
        self.root.title(self.APP_TITLE)
        self.root.geometry("350x500+20+50")
        self.root.configure(bg="#fffecb")
        #configure notebook tab style - use alt theme which supports background colors better
        style = ttk.Style()
        style.theme_use('alt')
        style.configure("TNotebook.Tab", background="#ebfdff", foreground="black", padding=[5, 2])
        style.map("TNotebook.Tab", background=[("selected", "#b0f6fc")], foreground=[("selected", "black")])
        #top frame for server IP and port
        topfrm = tk.Frame(self.root, relief=tk.GROOVE, borderwidth=2)
        tk.Label(topfrm, text="Server IP:").pack(side=tk.LEFT, padx=5, pady=5)
        self.ip_addr = tk.Label(topfrm, text=self.IP, width=15, anchor=tk.W)
        self.ip_addr.pack(side=tk.LEFT, padx=5, pady=5)
        tk.Label(topfrm, text="Port:").pack(side=tk.LEFT, padx=5, pady=5)
        self.port_entry = tk.Entry(topfrm, textvariable=self.portStr, width=5)
        self.port_entry.pack(side=tk.LEFT, padx=5, pady=5)      
        topfrm.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        #middle frame for Notebook
        midfrm = tk.Frame(self.root, relief=tk.GROOVE, borderwidth=2)
        self.notebook = ttk.Notebook(midfrm)
        self.notebook.add(self.keys_tab(), text="Keys")
        self.notebook.add(self.foto_tab(), text="Fotos")        
        self.notebook.pack(fill=tk.BOTH, expand=True)
        midfrm.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5)
        #botton frame for connect button
        botfrm = tk.Frame(self.root, relief=tk.GROOVE, borderwidth=2)
        self.connect_btn = tk.Button(botfrm, text="Start", height=1, width=10)
        self.connect_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        botfrm.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        #load options from file
        self.load_saved_path()

    def keys_tab(self):
        #add a sample tab to the notebook
        tab1 = tk.Frame(self.notebook)
        bodyfrm = tk.Frame(tab1)
        arrowKeyFrm = tk.Frame(bodyfrm, relief=tk.SUNKEN, borderwidth=1, bg="#bbefb5")
        tk.Label(arrowKeyFrm, text="Up", relief=tk.SOLID, borderwidth=1).grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        tk.Label(arrowKeyFrm, text="Left", relief=tk.SOLID, borderwidth=1).grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        tk.Label(arrowKeyFrm, text="Center", relief=tk.SOLID, borderwidth=1).grid(row=1, column=1, sticky="nsew", padx=5, pady=5)        
        tk.Label(arrowKeyFrm, text="Right", relief=tk.SOLID, borderwidth=1).grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        tk.Label(arrowKeyFrm, text="Down", relief=tk.SOLID, borderwidth=1).grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        for i in range(3):
            arrowKeyFrm.grid_rowconfigure(i, weight=1)
        for i in range(3):
            arrowKeyFrm.grid_columnconfigure(i, weight=1)
        arrowKeyFrm.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        optKeyFrm = tk.Frame(bodyfrm, relief=tk.SUNKEN, borderwidth=1, bg="#bbefb5")
        tk.Label(optKeyFrm, text="Key 1", relief=tk.SOLID, borderwidth=1).pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        tk.Label(optKeyFrm, text="Key 2", relief=tk.SOLID, borderwidth=1).pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        tk.Label(optKeyFrm, text="Key 3", relief=tk.SOLID, borderwidth=1).pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        tk.Label(optKeyFrm, text="Key 4", relief=tk.SOLID, borderwidth=1).pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        tk.Label(optKeyFrm, text="Key 5", relief=tk.SOLID, borderwidth=1).pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        optKeyFrm.pack(side=tk.BOTTOM, fill=tk.X, pady=2)
        bodyfrm.pack(fill=tk.BOTH, expand=True)
        return tab1

    def foto_tab(self):
        #add a second sample tab to the notebook
        tab2 = tk.Frame(self.notebook)        
        frm = tk.Frame(tab2, relief=tk.SUNKEN, borderwidth=1)
        self.canvas = tk.Canvas(frm, bg="#c3c3c3")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        infoFrm = tk.Frame(frm, relief=tk.SOLID, borderwidth=1)
        lblFrm = tk.Frame(infoFrm)
        self.image_label = tk.Label(lblFrm, text="No image")
        self.image_label.pack(side=tk.LEFT, padx=2)        
        lblFrm.pack(side=tk.TOP, fill=tk.X)
        btnFrm = tk.Frame(infoFrm)        
        tk.Button(btnFrm, text="Next", height=1, width=8, command=self.load_next_image).pack(side=tk.LEFT, padx=(0,5), pady=2)
        tk.Button(btnFrm, text="Delete", height=1, width=8, command=self.delete_current_image).pack(side=tk.LEFT, padx=(0,5), pady=2)
        self.files_lbl = tk.Label(btnFrm, text="No file selected")
        self.files_lbl.pack(side=tk.LEFT, padx=2)
        btnFrm.pack(side=tk.TOP, fill=tk.X, padx=2, pady=(0, 2))
        infoFrm.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)
        pathFrm = tk.Frame(infoFrm)
        tk.Button(pathFrm, text="Path", command=self.path_button_click).pack(side=tk.LEFT, padx=2)
        self.path_entry = tk.Entry(pathFrm, textvariable=self.pathStr, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=2)
        pathFrm.pack(side=tk.TOP, fill=tk.X, padx=2, pady=(0, 2))
        frm.pack(fill=tk.BOTH, expand=True)
        return tab2


    def load_pil_image(self, image_name):
        try:
            img = Image.open(image_name)
            img = img.resize((self.canvas.winfo_width(), self.canvas.winfo_height()), resample = Image.BILINEAR)
            return img
        except Exception as e:
            print(f"Error loading image: {e}")
            return None


    def get_file_info(self, file_name):
        filesize = os.path.getsize(file_name)
        file_info = f"{file_name}   Size:{filesize}"
        print(f"Selected: {file_name}")     
        self.image_label.config(text=file_info)


        
    def delete_current_image(self):
        if not self.path_files:
            return
        #confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this image?"):
            return
        del self.path_files[self.file_idx]
        if self.file_idx >= len(self.path_files):
            self.file_idx = len(self.path_files) - 1
        if self.path_files:
            self.load_next_image()
        else:
            self.canvas.delete("all")
            self.files_lbl.config(text="No file selected")
            self.image_label.config(text="No image")


    def load_next_image(self):
        # Implement the functionality for the Load button here
        file_path = filedialog.askopenfile( title="Open File",
                filetypes=[("Images", "*.png *.jpg *.jpeg"), ("All files", "*.*")] )
        if file_path:
            global tkimg
            self.file_name = file_path.name
            self.get_file_info(self.file_name)
            self.canvas.delete("all")
            #self.img = tk.PhotoImage(file=file_path.name)
            img = self.load_pil_image(self.file_name)
            if img is None:                
                self.canvas.create_text(10, 10, anchor=tk.NW, text="No Supported Image File")
                return
            tkimg = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=tkimg)


    def update_path_info(self):
        #count the files in path
        try:
            path = self.pathStr.get()
        except Exception as e:
            print(f"Error accessing path: {e}")
            return
        if os.path.isdir(path):
            self.path_files = os.listdir(path)
            #image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.file_idx = 0
            self.files_lbl.config(text=f"{self.file_idx} of {len(self.path_files)} files")
        else:
            self.path_files = []
            self.file_idx = 0
            self.files_lbl.config(text=f"{self.file_idx} of {len(self.path_files)} files")
        

    def path_button_click(self):
        file_path = filedialog.askdirectory(title="Select Directory")
        if file_path:
            self.pathStr.set(file_path)
            self.update_path_info()
            #save path to file OPT_FILE in application directory
            try:
                app_dir = os.path.dirname(os.path.abspath(__file__))
                opt_file_path = os.path.join(app_dir, self.OPT_FILE)
                with open(opt_file_path, "w") as f:
                    f.write(file_path)
            except Exception as e:
                print(f"Error saving path to {opt_file_path}: {e}")


    def load_saved_path(self):
        try:
            app_dir = os.path.dirname(os.path.abspath(__file__))
            opt_file_path = os.path.join(app_dir, self.OPT_FILE)
            if os.path.exists(opt_file_path):
                with open(opt_file_path, "r") as f:
                    file_path = f.read().strip()
                    if os.path.isdir(file_path):
                        self.pathStr.set(file_path)
                        self.update_path_info()
        except Exception as e:
            print(f"Error loading path from {opt_file_path}: {e}")


    def load_next_image(self):
        if not self.path_files:
            return
        self.file_idx = (self.file_idx + 1) % len(self.path_files)
        self.files_lbl.config(text=f"{self.file_idx} of {len(self.path_files)} files")
        self.file_name = os.path.join(self.pathStr.get(), self.path_files[self.file_idx])
        self.get_file_info(self.file_name)
        self.canvas.delete("all")
        img = self.load_pil_image(self.file_name)
        if img is None:
            self.canvas.create_text(10, 10, anchor=tk.NW, text="No Supported Image File")
            return
        global tkimg
        tkimg = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=tkimg)


    def run(self):
        self.root.mainloop()


#main function
if __name__ == '__main__':
    #open Gui
    mainWin=server_win()
    #...
    mainWin.run()
    print("End")          