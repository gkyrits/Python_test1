import tkinter as tk
from tkinter import ttk

class client_win:
    APP_TITLE = "Test Client"
    PORT = 8000
    IP = '127.0.0.1'

    def __init__(self):
        self.root = tk.Tk()
        self.ipStr = tk.StringVar(value=self.IP)
        self.portStr = tk.StringVar(value=str(self.PORT))         
        self.root.title(self.APP_TITLE)
        self.root.geometry("350x400+20+50")
        self.root.configure(bg="#fffecb")
        #top frame for server IP and port
        topfrm = tk.Frame(self.root, relief=tk.GROOVE, borderwidth=2)
        tk.Label(topfrm, text="Server IP:").pack(side=tk.LEFT, padx=5, pady=5)
        self.ip_entry = tk.Entry(topfrm, textvariable=self.ipStr, width=15)
        self.ip_entry.pack(side=tk.LEFT, padx=5, pady=5)
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
        self.connect_btn = tk.Button(botfrm, text="Connect", height=1, width=10)
        self.connect_btn.pack(side=tk.RIGHT, padx=5, pady=5)
        botfrm.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    def keys_tab(self):
        #add a sample tab to the notebook
        tab1 = tk.Frame(self.notebook)
        bodyfrm = tk.Frame(tab1)
        arrowKeyFrm = tk.Frame(bodyfrm, relief=tk.SUNKEN, borderwidth=1, bg="#bbefb5")
        tk.Button(arrowKeyFrm, text="Up").grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        tk.Button(arrowKeyFrm, text="Left").grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        tk.Button(arrowKeyFrm, text="Center").grid(row=1, column=1, sticky="nsew", padx=5, pady=5)        
        tk.Button(arrowKeyFrm, text="Right").grid(row=1, column=2, sticky="nsew", padx=5, pady=5)
        tk.Button(arrowKeyFrm, text="Down").grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        for i in range(3):
            arrowKeyFrm.grid_rowconfigure(i, weight=1)
        for i in range(3):
            arrowKeyFrm.grid_columnconfigure(i, weight=1)
        arrowKeyFrm.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        optKeyFrm = tk.Frame(bodyfrm, relief=tk.SUNKEN, borderwidth=1, bg="#bbefb5")
        tk.Button(optKeyFrm, text="Key 1").pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        tk.Button(optKeyFrm, text="Key 2").pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        tk.Button(optKeyFrm, text="Key 3").pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        tk.Button(optKeyFrm, text="Key 4").pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        tk.Button(optKeyFrm, text="Key 5").pack(side=tk.LEFT, expand=True, padx=2, pady=4)
        optKeyFrm.pack(side=tk.BOTTOM, fill=tk.X, pady=2)
        bodyfrm.pack(fill=tk.BOTH, expand=True)
        return tab1

    def foto_tab(self):
        #add a second sample tab to the notebook
        tab2 = tk.Frame(self.notebook)        
        frm = tk.Frame(tab2, relief=tk.SUNKEN, borderwidth=1)
        tk.Label(frm, text="Fotos").pack(padx=5, pady=5)
        frm.pack(fill=tk.BOTH, expand=True)
        return tab2

    def run(self):
        self.root.mainloop()

#main function
if __name__ == '__main__':
    #open Gui
    mainWin=client_win()
    #...
    mainWin.run()
    print("End")          