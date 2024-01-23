import tkinter as tk

WIN_TITLE = 'Test 4 V0.1'

def buildWin(frm,win):
        tk.Button(frm,text="Exit", command=win.destroy).place(relx=0.5, rely=0.5, relheight=0.5, relwidth=0.5, anchor=tk.CENTER)
        #tk.Button(frm,text="Exit", command=win.destroy).pack(padx=5, pady=5, side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

def buildWin1(frm,win):
    topfrm = tk.Frame(frm)
    tk.Button(topfrm,text="Win 1", command=but1_act, pady=30).pack(padx=5, pady=5, side=tk.LEFT, expand=tk.YES, fill=tk.X)
    tk.Button(topfrm,text="Win 2", command=but2_act, pady=30).pack(padx=5, pady=5, side=tk.LEFT, expand=tk.YES, fill=tk.X)
    tk.Button(topfrm,text="Win 3", command=but3_act, pady=30).pack(padx=5, pady=5, side=tk.LEFT, expand=tk.YES, fill=tk.X) 
    topfrm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
    tk.Button(frm,text="Exit", command=win.destroy, pady=20).pack(padx=5, pady=10, side=tk.TOP, expand=tk.YES, fill=tk.X)     


def test1(win,title=WIN_TITLE, id=1, fullscreen=0,geometry="320x240+0+0"):
    if(fullscreen):
        win.attributes('-fullscreen', True)
    else:
        win.title(title)
        win.geometry(geometry)
        win.resizable(False, False)
        #win.attributes("-toolwindow",1) //not supported in 3.9   
    frm=tk.Frame(win, relief=tk.GROOVE, borderwidth=2)
    if(id==1):
        buildWin1(frm,win)                        
    else:
        buildWin(frm,win)
    frm.pack(padx=5, pady=5, fill=tk.BOTH, expand=tk.YES)


def but1_act():    
    t1 = tk.Toplevel(bg="green")
    t1.attributes("-topmost",1)
    t1.overrideredirect(1)
    test1(t1,"Child Window",id=2,geometry="220x140+50+50")

def but2_act():
    pass

def but3_act():
    pass        

#---main---
root = tk.Tk()
root.config(bg="red")
test1(root,fullscreen=1)
#t1 = tk.Toplevel(root)
#t1.attributes("-topmost",1)
#test1(t1,"Child Window",id=2,geometry="320x240+200+200")
#t2 = tk.Toplevel(root)
#t2.attributes("-topmost",1)
#test1(t2,"Child Window *2*",id=3,geometry="320x240+400+400")
tk.mainloop()
print('End...')
