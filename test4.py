import tkinter as tk

#---class App---
class App:
    def __init__(self,root,win):
        tk.Button(root,text="Exit",command=win.destroy).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#---main---
root = tk.Tk()
root.title('Test 4 V0.1')
root.geometry("320x240+0+0")
tk.Button(root, text='Test').pack(padx=5, pady=5, fill=tk.BOTH)
#frm=tk.Frame(root, relief=tk.GROOVE, borderwidth=2).pack(padx=5, pady=5, fill=tk.BOTH)
#win = App(frm,root)
tk.mainloop()
print('End...')