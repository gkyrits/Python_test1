import tkinter as tk
from tkinter import ttk
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

tabs = ('Sensors', 'Options', 'Menu3')

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
    #release the keyboard grab first, so an error can never leave the screen without input
    def close():
        win.grab_release()
        win.destroy()
    def ok():
        try:
            if not all([func() for func in apply_funcs]):
                return
            opt.save()  #once, after every page stored its values
        except Exception as e:
            print('Fail apply options:', e)
        close()
    frm2=tk.Frame(win, bg=win_col)
    tk.Button(frm2, text="Ok", font=but_font, height=1, pady=0, command=ok).pack(side=tk.LEFT, pady=0, padx=5)
    tk.Button(frm2, text="Cancel", font=but_font, height=1, pady=0, command=close).pack(side=tk.LEFT, pady=0, padx=5)
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
    apply_funcs.append(options_page(p2))
    test_page(p3)
    nb.pack(padx=3, pady=0, fill=tk.BOTH, expand=1)      
    frm1.pack(side=tk.TOP,fill=tk.BOTH, expand=1)
    opt.grab_keyboard(win)  #key events for the offset entries


def test_page(win):
    tk.Label(win, text="This is a test page", font=win_font, bg=win_col2, pady=0, borderwidth=0, highlightthickness=0).pack(side=tk.TOP, anchor=tk.W)
    tk.Label(win, text="Text bla bla bla", font=win_font, bg=win_col2, pady=0, borderwidth=0, highlightthickness=0).pack(side=tk.TOP, anchor=tk.W)

# Options tab: language (frame 1), weather location select/add/delete/edit (frame 2)
lang_items = (('EN', opt.EN), ('GR', opt.GR))

def options_page(win):
    lbl = dict(font=win_font, bg=win_col2, padx=0, pady=0, borderwidth=0, highlightthickness=0)
    lblB = dict(lbl, font=win_fontB)
    btn = dict(font=win_font, padx=2, pady=0, borderwidth=1)
    frm_opt = dict(bg=win_col2, relief=tk.GROOVE, borderwidth=2)
    #--language frame, one choice only (checkbuttons sharing one variable)
    frm1 = tk.Frame(win, **frm_opt)
    tk.Label(frm1, text='Language', **lblB).pack(side=tk.LEFT, padx=2)
    lang_var = tk.IntVar(value=opt.LANG)
    for text, val in lang_items:
        tk.Checkbutton(frm1, text=text, variable=lang_var, onvalue=val, offvalue=val,
                       activebackground=win_col2, **lbl).pack(side=tk.LEFT, padx=4)
    frm1.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
    #--location frame
    frm2 = tk.Frame(win, **frm_opt)
    locs = {key: dict(loc) for key, loc in opt.locations.items()}  #edited copy, stored on Ok
    sel = [opt.LOCATION if opt.LOCATION in locs else next(iter(locs))]  #selected id
    tk.Label(frm2, text='Location', **lblB).grid(row=0, column=0, sticky=tk.W, padx=2)
    win.option_add('*TCombobox*Listbox.font', win_font)  #drop down list font
    combo = ttk.Combobox(frm2, state='readonly', width=18, font=win_font)
    combo.grid(row=0, column=1, columnspan=4, sticky=tk.W, padx=2, pady=1)
    ents = {}
    for name, text, width in (('name', 'Name', 14), ('lat', 'Lat', 8), ('lon', 'Lon', 8)):
        row = 1 if name == 'name' else 2
        c = 0 if name in ('name', 'lat') else 2
        tk.Label(frm2, text=text, **lbl).grid(row=row, column=c, sticky=tk.E, padx=2)
        ent = tk.Entry(frm2, width=width, font=win_font, borderwidth=1, highlightthickness=0)
        ent.grid(row=row, column=c+1, columnspan=3 if name == 'name' else 1, sticky=tk.W, padx=(1, 2), pady=1)
        #take the keyboard focus when the entry is touched
        ent.bind('<Button-1>', lambda e: e.widget.focus_force())
        ents[name] = ent

    def ids():
        return sorted(locs)
    def show(key):
        sel[0] = key
        combo['values'] = [locs[k]['name'] for k in ids()]
        combo.current(ids().index(key))
        for name, ent in ents.items():
            ent.delete(0, tk.END)
            ent.insert(0, str(locs[key][name]))  #str: all the lat/lon digits, '{:g}' keeps only 6
            ent.config(bg='white')
    #entries as a location, None (and pink entries) if a value is wrong
    def read_entries():
        loc = {'name': ents['name'].get().strip()}
        ok = bool(loc['name'])
        ents['name'].config(bg='white' if ok else 'pink')
        for name, limit in (('lat', 90), ('lon', 180)):
            try:
                loc[name] = float(ents[name].get().replace(',', '.'))
                if abs(loc[name]) > limit:
                    raise ValueError
                ents[name].config(bg='white')
            except ValueError:
                ents[name].config(bg='pink')
                ok = False
        return loc if ok else None
    #keep the edited entries in the selected location
    def store():
        loc = read_entries()
        if loc is None:
            return False
        locs[sel[0]] = loc
        return True
    def select(event):
        if store():
            show(ids()[combo.current()])
        else:
            combo.current(ids().index(sel[0]))  #fix the wrong values first
    def add():
        loc = read_entries()
        if loc is None:
            return
        #a name that exists (case ignored) only updates the lat/lon of that location
        same = [k for k in ids() if locs[k]['name'].casefold() == loc['name'].casefold()]
        if same:
            key = same[0]
            locs[key].update(lat=loc['lat'], lon=loc['lon'])
        else:
            key = max(locs) + 1
            locs[key] = loc
        show(key)
    def delete():
        if len(locs) > 1:
            pos = ids().index(sel[0])
            del locs[sel[0]]
            show(ids()[min(pos, len(locs)-1)])
    combo.bind('<<ComboboxSelected>>', select)
    tk.Button(frm2, text='Add', command=add, **btn).grid(row=3, column=1, sticky=tk.W, padx=2, pady=1)
    tk.Button(frm2, text='Del', command=delete, **btn).grid(row=3, column=3, sticky=tk.W, padx=2, pady=1)
    frm2.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
    show(sel[0])

    def apply():
        if not store():
            return False
        opt.LANG = lang_var.get()
        opt.locations = locs
        opt.LOCATION = sel[0]
        return True
    return apply

#edit sensors enable & offsets of options module, return a function that applies them
def sensors_page(win):
    lbl = dict(font=win_font, bg=win_col2, padx=0, pady=0, borderwidth=0, highlightthickness=0)
    lblB = dict(lbl, font=win_fontB)
    frm_opt = dict(bg=win_col2, relief=tk.GROOVE, borderwidth=2)
    #--enable frame, switches in one row
    en_frm = tk.Frame(win, **frm_opt)
    tk.Label(en_frm, text='Enable', **lblB).grid(row=0, column=0, sticky=tk.W, padx=2)
    en_vars = []
    for i, (name, text) in enumerate(sense_en_items):
        var = tk.IntVar(value=getattr(opt, name))
        tk.Checkbutton(en_frm, text=text, variable=var, activebackground=win_col2, **lbl).grid(row=0, column=1+i, sticky=tk.W, padx=4)
        en_vars.append((name, var))
    en_frm.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
    #--offset frame, one row per device
    off_frm = tk.Frame(win, **frm_opt)
    tk.Label(off_frm, text='Offset', **lblB).grid(row=0, column=0, sticky=tk.W, padx=2)
    entries = []
    for row, (device, items) in enumerate(offset_items, start=1):
        tk.Label(off_frm, text=device, **lbl).grid(row=row, column=0, sticky=tk.W, padx=4)
        for col, (text, name) in enumerate(items):
            tk.Label(off_frm, text=text, **lbl).grid(row=row, column=1+2*col, sticky=tk.E, padx=2)
            ent = tk.Entry(off_frm, width=5, font=win_font, borderwidth=1, highlightthickness=0)
            ent.insert(0, '{:g}'.format(getattr(opt, name)))
            ent.grid(row=row, column=2+2*col, sticky=tk.W, padx=(1, 2), pady=1)
            #take the keyboard focus when the entry is touched
            ent.bind('<Button-1>', lambda e: e.widget.focus_force())
            entries.append((name, ent))
    off_frm.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)

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
