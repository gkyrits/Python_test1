import tkinter as tk
import time as tm
import threading as thrd

run_count=0
thrd_exit=False

class main_win:
    def __init__(self,title):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("200x200+100+100")
        tk.Label(self.root,text="Hello!").pack(side="top")
        self.count=tk.Label(self.root,text="1",font="Arial 60 bold",fg="red")
        self.count.pack(side="left",padx=10,pady=10)
        tk.Button(self.root,text="Exit",command=self.root.destroy).pack(side="bottom")

    def __str__(self):
        return "main_win class"
    
    def set_count(self,cnt):
        self.count.config(text=int(cnt))

    def run(self):
        self.root.mainloop()

def count_thread(tmout):
    global run_count,win,exit
    while True:
        tm.sleep(tmout)
        if thrd_exit:
            break        
        run_count += 1
        win.set_count(run_count)


#main
print("Test App")
win=main_win("Test App")
print(win)
#start thread...
t=thrd.Thread(target=count_thread,args=[0.3])
t.start()
#start win...
win.run()
thrd_exit=True
t.join()
print("End...")