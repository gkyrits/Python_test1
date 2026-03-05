import tkinter as tk
import subprocess as proc

class MonitorSet:
    WIDTH="400"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Monitor Settings")
        self.root.geometry(self.WIDTH+"x200+100+100")
        self.root.resizable(False, False)
        #self.root.attributes('-toolwindow', 1)
        # Brightness
        frm1=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm1,text="Brightness").pack(side="top")
        self.bright_scale = tk.Scale(frm1,from_=0,to=100, orient=tk.HORIZONTAL)
        self.bright_scale.pack(side="top", fill=tk.X, padx=4, pady=0)
        frm1.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
        # Contrast
        frm2=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm2,text="Contrast").pack(side="top")
        self.contrast_scale = tk.Scale(frm2,from_=0,to=100,orient=tk.HORIZONTAL)
        self.contrast_scale.pack(side="top", fill=tk.X, padx=4, pady=0)
        frm2.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
        # Resize height
        self.root.update()
        height=frm1.winfo_height()+frm2.winfo_height()
        self.root.geometry("{}x{}+100+100".format(self.WIDTH, height+4*4))
        # scale events
        self.bright_scale.configure(command=self.brightness_changed)
        self.contrast_scale.configure(command=self.contrast_changed)

    def brightness_changed(self,val):
        print("Brightness:",val)
        proc.run(["brightnessctl","set","{}%".format(val)])

    def contrast_changed(self,val):
        print("Contrast:",val)
        proc.run(["xgamma","-gamma","{}".format(int(val)/100)])

    def set_brightness(self,val):
        self.bright_scale.set(int(val)) 

    def set_contrast(self,val):
        self.contrast_scale.set(float(val)*100)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    print("Monitor Settings App")
    app=MonitorSet()
    #read brightness value
    brightness = proc.check_output(["brightnessctl","get"]).decode().strip()
    print("Current Brightness:", brightness)
    app.set_brightness(brightness)
    #read contrast value
    contrast = proc.check_output(["xgamma"], stderr=proc.STDOUT).decode().strip().split(" ")[3].split(",")[0]
    print("Current Contrast:", contrast)
    app.set_contrast(contrast)
    app.run()
    print("End...")