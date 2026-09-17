import tkinter as tk
import Pmw as tk2


LCD_SIZE = '320x240'
FULL_SCREEN = 0

win_col = 'DarkSeaGreen1'
win_col2 = "light yellow"
tab_col = "light steel blue"

win_font=('Arial', 7)
win_fontB=('Arial', 7, 'bold')
but_font=('Arial', 8, 'bold')

tabs = ('Menu1', 'Menu2', 'Menu3')

def draw_form(win):
    win.config(bg=win_col)
    #add buttons_frm ======
    frm2=tk.Frame(win, bg=win_col)
    tk.Button(frm2, text="Ok", font=but_font, height=1, pady=0, command=win.destroy).pack(side=tk.LEFT, pady=0, padx=5)
    tk.Button(frm2, text="Cancel", font=but_font, height=1, pady=0, command=win.destroy).pack(side=tk.LEFT, pady=0, padx=5)
    frm2.pack(side=tk.BOTTOM, anchor=tk.E, pady=1)
    #add main_frm ======
    frm1=tk.Frame(win, bg=win_col)
    nb = tk2.NoteBook(frm1, borderwidth=1, pagemargin=2)
    p1=nb.add(tabs[0], tab_height=1, tab_pady=0, page_pady=0)
    p2=nb.add(tabs[1], tab_height=1, tab_pady=0, page_pady=0)
    p3=nb.add(tabs[2], tab_height=1, tab_pady=0, page_pady=0)
    for page_name in tabs:
        nb.tab(page_name).configure(font=win_fontB, background=tab_col)
        nb.page(page_name).configure(background=win_col2)
    nb.component('hull').configure(background=win_col)
    test_page(p1)
    test_page(p2)
    test_page(p3)
    nb.pack(padx=3, pady=0, fill=tk.BOTH, expand=1)      
    frm1.pack(side=tk.TOP,fill=tk.BOTH, expand=1)


def test_page(win):
    tk.Label(win, text="This is a test page", font=win_font, bg=win_col2, pady=0, borderwidth=0, highlightthickness=0).pack(side=tk.TOP, anchor=tk.W)
    tk.Label(win, text="Text bla bla bla", font=win_font, bg=win_col2, pady=0, borderwidth=0, highlightthickness=0).pack(side=tk.TOP, anchor=tk.W)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Option Menu')
    root.geometry(LCD_SIZE+'+0+0')
    if FULL_SCREEN:
        root.overrideredirect(1)    
    
    draw_form(root)
    root.mainloop()
    print('End of program')