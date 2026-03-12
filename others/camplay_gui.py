import tkinter as tk
import Pmw as tk2
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
        tk2.initialise(self.root)
        self.root.title(title)
        self.root.geometry("400x200+20+50")
        #add buttons_frm ======
        frm2=tk.Frame(self.root)
        tk.Button(frm2, text="Update").pack(side=tk.LEFT, padx=5)
        tk.Button(frm2, text="Open").pack(side=tk.LEFT, padx=5)
        #add cam ListBox ------
        cbx_entries = ('cam 1','cam 2','cam 3')
        cbx = tk2.ComboBox(frm2, label_text='Cam:', labelpos='w', listheight=60, dropdown=1, scrolledlist_items=cbx_entries)
        cbx.selectitem(cbx_entries[0])
        cbx.pack(side=tk.LEFT)
        frm2.pack(side=tk.BOTTOM, anchor=tk.W, pady=5)
        #add text_frm ======
        tk.Label(self.root, text="Available Cameras").pack(side=tk.TOP)
        frm1=tk.Frame(self.root, relief=tk.GROOVE,  borderwidth=2)                
        text=tk.Text(frm1, height=30)
        scroll = tk.Scrollbar(frm1, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        #fill text info
        txtio = io.StringIO('')
        pprint(demo_obj, out=txtio)
        text.insert(tk.END, txtio.getvalue())
        text.config(state=tk.DISABLED)
        #pack frm1
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(side=tk.LEFT,fill=tk.BOTH)        
        frm1.pack(side=tk.TOP,fill=tk.X)



    def run(self):
        self.root.mainloop() 


#main function
if __name__ == '__main__':
    print(APP_TITLE+" start...")    
    txtio = io.StringIO('')
    pprint(demo2_obj, out=txtio)
    print(txtio.getvalue(), end='')
    win=main_win(APP_TITLE+" V0.1")
    #...
    win.run()
    print("End")