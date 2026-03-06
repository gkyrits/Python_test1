import tkinter as tk
import subprocess as proc

#set working directory to script location
import sys
import os
dir=os.path.dirname(os.path.realpath(__file__))
os.chdir(dir)

class MonitorSet:
    WIDTH="400"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Monitor Settings")
        self.root.geometry(self.WIDTH+"x200+100+100")
        self.root.resizable(False, False)
        #self.root.attributes('-toolwindow', 1)
        # Brightness
        global img1
        img1=tk.PhotoImage(file="sun_24.png")
        frm1=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm1,image=img1).pack(side=tk.LEFT)
        self.bright_scale = tk.Scale(frm1,from_=0,to=100, orient=tk.HORIZONTAL)
        self.bright_scale.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=4, pady=0)
        frm1.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
        # Contrast
        global img2
        img2=tk.PhotoImage(file="contrast_24.png")
        frm2=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)
        tk.Label(frm2,image=img2).pack(side=tk.LEFT)
        self.contrast_scale = tk.Scale(frm2,from_=0,to=100,orient=tk.HORIZONTAL)
        self.contrast_scale.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=4, pady=0)
        frm2.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
        # Resize height
        self.root.update()
        height=frm1.winfo_height()+frm2.winfo_height()
        self.root.geometry("{}x{}+100+100".format(self.WIDTH, height+4*4))
        # scale events
        self.bright_scale.configure(command=self.brightness_changed)
        self.contrast_scale.configure(command=self.contrast_changed)

    #function range 0-100 to 0-255    
    def val_to_255(self,val):
        return int(val * 255 / 100)
    
    #function range 0-255 to 0-100
    def val_to_100(self,val):
        return int(val * 100 / 255)

    #brightness change event
    def brightness_changed(self,val):
        val = self.val_to_255(int(val))
        print("Brightness:",val)
        try:
            proc.run(["brightnessctl","set","{}".format(val)])
        except:
            print("Error occurred while setting brightness")

    #contrast change event
    def contrast_changed(self,val):
        print("Contrast:",val)
        try:
            proc.run(["xgamma","-gamma","{}".format(int(val)/100)])
        except:
            print("Error occurred while setting contrast")

    #set brightness value
    def set_brightness(self,val):
        val = self.val_to_100(int(val))
        self.bright_scale.set(int(val)) 

    #set contrast value
    def set_contrast(self,val):
        self.contrast_scale.set(float(val)*100)

    #run the app
    def run(self):
        self.root.mainloop()


#main function
if __name__ == '__main__':
    print("Monitor Settings App")
    app=MonitorSet()

    #read brightness value
    try:
        brightness = proc.check_output(["brightnessctl","get"]).decode().strip()
        print("Current Brightness:", brightness)
        app.set_brightness(brightness)
    except:
        print("Error occurred while reading brightness")
    #read contrast value
    try:
        contrast = proc.check_output(["xgamma"], stderr=proc.STDOUT).decode().strip().split(" ")[3].split(",")[0]
        print("Current Contrast:", contrast)
        app.set_contrast(contrast)
    except:
        print("Error occurred while reading contrast")

    app.run()
    print("End...")