import tkinter as tk

wroot = tk.Tk()
wroot.title("test3 v01")
tk.Label(wroot, text="main window").pack(pady=1)
wroot.geometry("600x150+300+350")

#wch1 = tk.Toplevel(wroot)
#tk.Label(wch1, text="child 1 window" ).pack(padx=5, pady=10) 

#wch2 = tk.Toplevel(wroot)
#wch2.transient(wroot) 
#tk.Label(wch2, text="child 2 window" ).pack(padx=5, pady=10)

wch3 = tk.Toplevel(wroot, borderwidth=1, bg="green")
tk.Label(wch3, text="child 3 window" ).pack(padx=80, pady=50)
tk.Button(wch3, text="Exit", width=20, command=wch3.destroy).pack(side=tk.LEFT, padx=10)
wch3.overrideredirect(1)
wch3.geometry("400x200+100+100")

for relief in [tk.RAISED, tk.SUNKEN, tk.FLAT, tk.RIDGE, tk.GROOVE, tk.SOLID]:
    f = tk.Frame(wroot, borderwidth=2, relief=relief)
    tk.Label(f, text=relief, width=10).pack(side=tk.LEFT)
    f.pack(side=tk.LEFT, padx=5, pady=5)

wroot.mainloop()
print("End...")

