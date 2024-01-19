import tkinter as tk
import tkinter.ttk as ttk


#MyLabel class
class MyLabel(ttk.Label):
    def __init__(self, parent, text='MyLabel',**kwargs):
        super().__init__(parent,text=text,**kwargs)        
        self.pack()

#App class code -------
class App:
    """ App class"""
    def __init__(self):
        """ construct """
        self.root = tk.Tk()
        self.root.title("Test App V0.1")
        tk.Label(self.root, text="Hello!").pack()
        ttk.Label(self.root, text="New Hello!").pack()
        tk.Button(self.root, text="Button").pack()
        ttk.Button(self.root, text="Button2").pack()
        MyLabel(self.root,text="..1..",font="Arial 12")
        MyLabel(self.root,font="Arial 15")

    def __str__(self):
        """ description """
        return "main App Window"

    def run(self):
        """ run method """
        self.root.mainloop()

#main code ----
app = App()
print("Type of app :"+str(type(app)))
print(app)
print("---")
print("Running...")
app.run()
print("End!")


