import tkinter as tk

#---class App---
class App:
    def __init__(self,frm,win):
        tk.Button(frm,text="Exit",command=win.destroy).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#---main---
root = tk.Tk()
root.title('Test 4 V0.1')
root.geometry("320x240+0+0")
#root.overrideredirect=1
frm=tk.Frame(root, relief=tk.GROOVE, borderwidth=2, height=1000).pack(padx=5, pady=5, fill=tk.BOTH)
win = App(frm,root)
tk.mainloop()
print('End...')