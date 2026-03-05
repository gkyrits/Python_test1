import tkinter as tk

def weather_panel(parent):
    global img
    tk.Label(parent, text="Weather...", width=30).pack(side=tk.TOP, padx=5, pady=5)
    test_img='13.png'
    img = tk.PhotoImage(file=test_img)
    tk.Label(parent, image=img).pack(side=tk.TOP)

root = tk.Tk()
root.title('PythonGuides')

weather_panel(root)

root.mainloop()