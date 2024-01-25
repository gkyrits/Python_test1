import tkinter as tk

WIN_TITLE = 'Test 4 V0.1'

def buildWin1(frm,win):
        bg_col="yellow"
        frm.config(bg=bg_col)
        tk.Button(frm,text="Exit", command=win.destroy).place(relx=0.5, rely=0.5, relheight=0.5, relwidth=0.5, anchor=tk.CENTER)
        tk.Label(frm,text="Window 1", bg=bg_col, font="Bold").pack(side=tk.TOP)
        #tk.Button(frm,text="Exit", command=win.destroy).pack(padx=5, pady=5, side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

def buildWin0(frm,win):
    bg_col="#b8f0ff"
    frm.config(bg=bg_col)
    topfrm = tk.Frame(frm,bg=bg_col)
    tk.Button(topfrm,text="Win 1", command=but1_act, pady=30).pack(padx=5, pady=5, side=tk.LEFT, expand=tk.YES, fill=tk.X)
    tk.Button(topfrm,text="Win 2", command=but2_act, pady=30).pack(padx=5, pady=5, side=tk.LEFT, expand=tk.YES, fill=tk.X)
    tk.Button(topfrm,text="Win 3", command=but3_act, pady=30).pack(padx=5, pady=5, side=tk.LEFT, expand=tk.YES, fill=tk.X) 
    topfrm.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
    tk.Button(frm,text="Exit", command=win.destroy, pady=20).pack(padx=5, pady=10, side=tk.TOP, expand=tk.YES, fill=tk.X)

def scale_change(value,lbl):
    lbl.config(text=value)

def buildWin2(frm,win):
    leftfrm = tk.Frame(frm, bg="green")
    lbl = tk.Label(leftfrm,text="0",font="Bold")    
    lbl.pack(padx=5, side=tk.TOP)
    tk.Scale(leftfrm, to=255, tickinterval=100, orient=tk.VERTICAL, showvalue=0, length=500, command=lambda x,l=lbl :scale_change(x,lbl) )\
        .pack(padx=5, pady=2, side=tk.TOP)
    leftfrm.pack(side=tk.LEFT, fill=tk.Y)
    rightfrm = tk.Frame(frm, bg="yellow")
    tk.Button(rightfrm,text="Exit", command=win.destroy).pack(padx=5, pady=5, side=tk.BOTTOM, fill=tk.X)
    rightfrm.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)



def test1(win,title=WIN_TITLE, id=0, fullscreen=0,geometry="320x240+0+0"):
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
    elif(id==2):
        buildWin2(frm,win)
    else:
        buildWin0(frm,win)    
    frm.pack(padx=5, pady=5, fill=tk.BOTH, expand=tk.YES)


def but1_act():    
    t1 = tk.Toplevel(bg="green")
    t1.attributes("-topmost",1)
    t1.overrideredirect(1)
    test1(t1,"Child Window 1",id=1,geometry="220x140+50+50")

def but2_act():
    t1 = tk.Toplevel(bg="blue")
    t1.attributes("-topmost",1)
    t1.overrideredirect(1)
    test1(t1,"Child Window 2",id=2,geometry="220x200+50+50")    

def but3_act():
    pass        

#---main---
root = tk.Tk()
root.config(bg="red")
test1(root,fullscreen=0)
tk.mainloop()
print('End...')
