import tkinter as tk
import Pmw as tk2
import options as opt


LCD_SIZE = opt.LCD_SIZE
FULL_SCREEN = opt.FULL_SCREEN

win_col = 'DarkSeaGreen1'
win_col2 = "light yellow"
tab_col = "light steel blue"
tab_sel_col = "#dfe7f1"  # selected tab, lighter than tab_col

win_font=('Arial', 7)
win_fontB=('Arial', 7, 'bold')
but_font=('Arial', 8, 'bold')

tabs = ('Sensors', 'Menu2', 'Menu3')

# Sensors tab: (options name, text) of the enable switches
sense_en_items = (('SENSE1_EN', 'S1'), ('SENSE2_EN', 'S2'), ('SENSE3_EN', 'S3'))
# Sensors tab: offsets per device, (text, options name)
offset_items = (('Sense HAT', (('T', 'SENSEHAT_TEMP_OFFSET'), ('H', 'SENSEHAT_HUMID_OFFSET'),
                               ('PT', 'SENSEHAT_PRESS_TEMP_OFFSET'), ('P', 'SENSEHAT_PRESS_OFFSET'))),
                ('AHT10',     (('T', 'AHT10_TEMP_OFFSET'), ('H', 'AHT10_HUMID_OFFSET'))),
                ('SI7021',    (('T', 'SI7021_TEMP_OFFSET'), ('H', 'SI7021_HUMID_OFFSET'))),
                ('MPL3115',   (('T', 'MPL3115_TEMP_OFFSET'), ('P', 'MPL3115_PRESS_OFFSET'),
                               ('A', 'MPL3115_ALTIT_OFFSET'))))

def draw_form(win):
    win.config(bg=win_col)
    #keys straight to the entries, without the X input method popup box
    win.tk.call('tk', 'useinputmethods', '-displayof', win, 0)
    #add buttons_frm ======
    apply_funcs=[]  #page functions that store the edited values, False if a value is wrong
    def ok():
        if all([func() for func in apply_funcs]):
            win.destroy()
    frm2=tk.Frame(win, bg=win_col)
    tk.Button(frm2, text="Ok", font=but_font, height=1, pady=0, command=ok).pack(side=tk.LEFT, pady=0, padx=5)
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
    #lighter color on the selected tab
    def tab_select(page_name):
        for name in tabs:
            col = tab_sel_col if name == page_name else tab_col
            nb.tab(name).configure(background=col, activebackground=col)
    nb.configure(raisecommand=tab_select)
    tab_select(nb.getcurselection())
    apply_funcs.append(sensors_page(p1))
    test_page(p2)
    test_page(p3)
    nb.pack(padx=3, pady=0, fill=tk.BOTH, expand=1)      
    frm1.pack(side=tk.TOP,fill=tk.BOTH, expand=1)
    opt.grab_keyboard(win)  #key events for the offset entries


def test_page(win):
    tk.Label(win, text="This is a test page", font=win_font, bg=win_col2, pady=0, borderwidth=0, highlightthickness=0).pack(side=tk.TOP, anchor=tk.W)
    tk.Label(win, text="Text bla bla bla", font=win_font, bg=win_col2, pady=0, borderwidth=0, highlightthickness=0).pack(side=tk.TOP, anchor=tk.W)

#edit sensors enable & offsets of options module, return a function that applies them
def sensors_page(win):
    lbl = dict(font=win_font, bg=win_col2, padx=0, pady=0, borderwidth=0, highlightthickness=0)
    lblB = dict(lbl, font=win_fontB)
    #enable switches, one row
    tk.Label(win, text='Enable', **lblB).grid(row=0, column=0, sticky=tk.W)
    en_vars = []
    for i, (name, text) in enumerate(sense_en_items):
        var = tk.IntVar(value=getattr(opt, name))
        tk.Checkbutton(win, text=text, variable=var, activebackground=win_col2, **lbl).grid(row=0, column=1+2*i, columnspan=2, sticky=tk.W)
        en_vars.append((name, var))
    #offsets, one row per device
    tk.Label(win, text='Offset', **lblB).grid(row=1, column=0, sticky=tk.W)
    entries = []
    for row, (device, items) in enumerate(offset_items, start=2):
        tk.Label(win, text=device, **lbl).grid(row=row, column=0, sticky=tk.W, padx=4)
        for col, (text, name) in enumerate(items):
            tk.Label(win, text=text, **lbl).grid(row=row, column=1+2*col, sticky=tk.E, padx=2)
            ent = tk.Entry(win, width=5, font=win_font, borderwidth=1, highlightthickness=0)
            ent.insert(0, '{:g}'.format(getattr(opt, name)))
            ent.grid(row=row, column=2+2*col, sticky=tk.W, padx=(1, 2), pady=1)
            #take the keyboard focus when the entry is touched
            ent.bind('<Button-1>', lambda e: e.widget.focus_force())
            entries.append((name, ent))

    def apply():
        values = {}
        for name, ent in entries:
            try:
                values[name] = float(ent.get().replace(',', '.'))
                ent.config(bg='white')
            except ValueError:
                ent.config(bg='pink')  #not a number, keep the form open
        if len(values) != len(entries):
            return False
        for name, val in values.items():
            setattr(opt, name, val)
        for name, var in en_vars:
            setattr(opt, name, var.get())
        opt.save()
        return True
    return apply

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Option Menu')
    root.geometry(LCD_SIZE+'+0+0')
    opt.full_screen(root)    
    
    draw_form(root)
    root.mainloop()
    print('End of program')
