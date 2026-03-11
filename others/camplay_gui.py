import tkinter as tk
import time as tm
import threading as thrd
import sys
import io

APP_TITLE = "Cam Play"

demo_obj  = [{'name':'alfa','number':3},{'name':'bhta','number':10,'id':1}]
demo2_obj = ({'name':'alfa','number':3},{'name':'bhta','number':10,'id':1})

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
        self.root.title(title)
        self.root.geometry("400x200+20+50")
        #add buttons_frm
        frm2=tk.Frame(self.root)
        tk.Button(frm2, text="Update").pack(side=tk.LEFT, padx=5)
        tk.Button(frm2, text="Open Cam").pack(side=tk.LEFT, padx=5)
        #add cam ListBox
        cbx = tk.Listbox(frm2, height=1, width=3)
        cbx_scrl = tk.Scrollbar(frm2, command=cbx.yview)
        cbx.configure(yscrollcommand=cbx_scrl.set)
        cbx.pack(side=tk.LEFT)
        cbx_scrl.pack(side=tk.RIGHT, fill=tk.Y)
        for item in range(3):
            cbx.insert(tk.END, item)
        frm2.pack(side=tk.BOTTOM, anchor=tk.W, pady=5)
        #add text_frm
        tk.Label(self.root, text="Available Cameras").pack(side=tk.TOP)
        frm1=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)                
        text=tk.Text(frm1, height=30)
        scroll = tk.Scrollbar(frm1, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        #...
        text.insert(tk.END, "some text ...\n")
        #for x in range(30) :
        #    text.insert(tk.END, "line "+str(x)+" !\n")
        txt = io.StringIO('')
        pprint(demo_obj, out=txt)
        text.insert(tk.END, txt.getvalue())
        text.config(state=tk.DISABLED)
        #...
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT,fill=tk.BOTH)        
        frm1.pack(side=tk.TOP,fill=tk.X)



    def run(self):
        self.root.mainloop() 


#main function
if __name__ == '__main__':
    print(APP_TITLE+" start...")
    txt = io.StringIO('')
    pprint(demo2_obj, out=txt)
    print(txt.getvalue(), end='')
    win=main_win(APP_TITLE+" V0.1")
    #...
    win.run()
    print("End")