import tkinter as tk

LCD_SIZE = "320x240"
FULL_SCREEN = 1

#======== Gui Calss =========
class Gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("raspi play v0.1")
        self.root.geometry(LCD_SIZE+'+0+0')
        if(FULL_SCREEN):
              self.root.overrideredirect(1)  
        self.init_clock_window()

    def __str__(self):
        """ description """
        return "Gui Class"        

    def run(self):
        self.root.mainloop()

    def update_clock(self,time):
        time_part = time.split(":")
        main_time = time_part[0]+":"+time_part[1]
        sec_time = ":"+time_part[2]        
        self.clkmain_lbl.config(text=main_time)
        self.clksec_lbl.config(text=sec_time)
        #self.root.update()

    def init_clock_window(self):
        #--panel buttons--
        win_col = "light yellow"
        pnl_bt_col = "pink"
        pnlfrm =  tk.Frame(self.root, bg=win_col)
        tk.Button(pnlfrm,text="K1", bg=pnl_bt_col).pack(side=tk.TOP, expand=tk.YES)
        tk.Button(pnlfrm,text="K2", bg=pnl_bt_col).pack(side=tk.TOP, expand=tk.YES)
        tk.Button(pnlfrm,text="K3", bg=pnl_bt_col, command=self.root.destroy).pack(side=tk.TOP, expand=tk.YES)
        pnlfrm.pack(side=tk.LEFT, fill=tk.Y)
        #--panel right
        pnlother =  tk.Frame(self.root, bg=win_col, relief=tk.GROOVE, borderwidth=2)
        #--panel clock
        clk_bg = "light steel blue"
        clk_fg = "blue"
        clkfrm = tk.Frame(pnlother, bg=clk_bg)
        self.clkmain_lbl = tk.Label(clkfrm, text="00:00", fg=clk_fg, bg=clk_bg, font="Arial 60 bold")
        self.clkmain_lbl.pack(side=tk.LEFT)
        self.clksec_lbl = tk.Label(clkfrm, text=":00", fg=clk_fg, bg=clk_bg, font="Arial 30 bold")
        self.clksec_lbl.pack(side=tk.LEFT, pady=10, anchor=tk.S)
        clkfrm.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)
        #---
        pnlother.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
        
        
#======== Main ============
        
gui = Gui()
gui.update_clock("13:24:32")
gui.run()
print("End...")