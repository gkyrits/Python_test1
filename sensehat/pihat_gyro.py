import math
import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
from PIL import Image, ImageTk

# Module της 3D σκηνής: για άλλη 3D βιβλιοθήκη αλλάζει μόνο αυτό το import
# (το module πρέπει να δίνει GyroScene με το ίδιο interface, βλ. pi3d_gyro.py)
import pi3d_gyro as gyro3d

# Σχεδίαση πυξίδας (Compass) και διανυσμάτων X/Y/Z (Magnetometer, Accelerometer) σε Tk Canvas
import compass
import xyz_force

try:
    from sense_hat import SenseHat
except ImportError:
    try:
        from sense_emu import SenseHat
    except ImportError:
        SenseHat = None


def euler_to_matrix(angles):
    # Πίνακας περιστροφής από roll/pitch/yaw (μοίρες), με τη σύμβαση της Sense HAT
    # (RTIMULib, aerospace Z-Y-X): R = Rz(yaw) · Ry(pitch) · Rx(roll)
    r, p, y = (math.radians(angles[name]) for name in ("roll", "pitch", "yaw"))
    cr, sr, cp, sp, cy, sy = math.cos(r), math.sin(r), math.cos(p), math.sin(p), math.cos(y), math.sin(y)
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
                     [-sp,     cp * sr,                cp * cr]])


def matrix_to_euler(m):
    # Αντίστροφο του euler_to_matrix: roll, yaw στο -180..180, pitch στο -90..90
    pitch = math.asin(max(-1.0, min(1.0, -m[2, 0])))
    roll = math.atan2(m[2, 1], m[2, 2])
    yaw = math.atan2(m[1, 0], m[0, 0])
    return {"roll": math.degrees(roll), "pitch": math.degrees(pitch), "yaw": math.degrees(yaw)}


WINDOW_TITLE = "Sense Gyroscope"

CANVAS_BG_COLOR = "light gray"
CANVAS_WIDTH = 350
CANVAS_HEIGHT = 250
MAGNET_RANGE = 100.0  # µT στο άκρο των αξόνων (γήινο πεδίο ~25-65 µT)
ACCEL_RANGE = 2.0  # g στο άκρο των αξόνων (σε ηρεμία |a| ≈ 1 g, η βαρύτητα)
# Επιλογές κλίμακας (g) και αρχική τιμή, ξεχωριστά για τον σταυρό X/Y και τον Z
ACCEL_RANGE_CHOICES = {"range_xy": ((0.1, 0.5, 1.0, 1.5, 2.0), 1.0),
                       "range_z": ((0.5, 1.0, 1.5, 2.0), 2.0)}

# Προειδοποίηση έντασης πεδίου (µT) για πειράματα με μαγνήτη
FIELD_WARN = 150.0
FIELD_DANGER = 300.0
FIELD_WARN_COLOR = "#d07000"  # σκούρο πορτοκαλί, ευανάγνωστο σε ανοιχτό φόντο


# ΟΡΙΣΤΕ ΕΔΩ ΤΙΣ ΑΝΕΞΑΡΤΗΤΕΣ ΔΙΑΣΤΑΣΕΙΣ του σχήματος (μήκος, ύψος, βάθος)
SHAPE_SIZE = (1.6, 0.2, 1.0)


class Transparent3DCubeApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)

        if SenseHat is not None:
            self.sense = SenseHat()
            self.sense.clear()
        else:
            self.sense = None
        self.sensor = None  # τελευταία ανάγνωση του αισθητήρα (για το calibrate)

        # 1. Η 3D σκηνή (σχήμα, άξονες, γράμματα) από το module gyro3d
        self.scene = gyro3d.GyroScene(CANVAS_WIDTH, CANVAS_HEIGHT, shape_size=SHAPE_SIZE, title=WINDOW_TITLE)

        # Notebook με μικρά tabs (ίδια γραμματοσειρά με το υπόλοιπο GUI, μικρό ύψος tab)
        style = ttk.Style(root)
        style.configure("Small.TNotebook", tabmargins=(2, 2, 2, 0))
        style.configure("Small.TNotebook.Tab", font="TkDefaultFont", padding=(6, 0))
        notebook = ttk.Notebook(root, style="Small.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True)
        gyro_tab = tk.Frame(notebook)
        notebook.add(gyro_tab, text="Gyroscope")
        compass_tab = tk.Frame(notebook)
        notebook.add(compass_tab, text="Compass")
        magnet_tab = tk.Frame(notebook)
        notebook.add(magnet_tab, text="Magnetometer")
        # Κενό (προς το παρόν) tab
        accel_tab = tk.Frame(notebook)
        notebook.add(accel_tab, text="Accelerometer")
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.notebook, self.gyro_tab, self.compass_tab = notebook, gyro_tab, compass_tab
        self.magnet_tab, self.accel_tab = magnet_tab, accel_tab

        # 2. Στήσιμο του Tkinter GUI Canvas (στο tab Gyroscope)
        # Ο canvas ακολουθεί το μέγεθος του παραθύρου, και η 3D σκηνή τον canvas
        # shape_frame: αριστερά το tool_frame με τα κουμπιά, δεξιά ο canvas
        # (pack στο τέλος, μετά τα πλαίσια του κάτω μέρους, ώστε να παίρνει τον χώρο που μένει)
        shape_frame = tk.Frame(gyro_tab)
        tool_frame = tk.Frame(shape_frame)
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        self.tool_buttons = {}
        # R = reset offsets, C = calibrate (το σχήμα γίνεται 0,0,0)
        tool_commands = {"M": None, "R": self.reset_offsets, "C": self.calibrate}
        for text, command in tool_commands.items():
            button = tk.Button(tool_frame, text=text, width=2, height=2, padx=0, pady=0, command=command)
            button.pack(side=tk.TOP, pady=(10, 0))
            self.tool_buttons[text] = button
        self.canvas = tk.Canvas(shape_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=CANVAS_BG_COLOR, highlightthickness=0)

        self.angle_titles = {"roll": "Roll (X)", "pitch": "Pitch (Y)", "yaw": "Yaw (Z)"}

        # 4. Πλαίσιο με sliders: τιμές προσανατολισμού χωρίς Sense HAT, αλλιώς offsets
        # (pack πρώτο με side=BOTTOM ώστε να βρίσκεται κάτω από το info_frame)
        control_frame = tk.Frame(gyro_tab, relief=tk.SUNKEN, borderwidth=2)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        control_frame.columnconfigure(1, weight=1)
        title = "Orientation values" if self.sense is None else "Orientation offsets"
        tk.Label(control_frame, text=title, font="TkDefaultFont 9 bold").grid(
            row=0, column=0, columnspan=3, sticky=tk.W, padx=2)
        self.scale_vars = {}
        for row, (name, angle_title) in enumerate(self.angle_titles.items(), start=1):
            # Βήμα 0.1° ώστε το calibrate να φτάνει το σχήμα πρακτικά ακριβώς στο 0
            var = tk.DoubleVar(value=0.0)
            value_label = tk.Label(control_frame, text="0.0°", width=7, anchor=tk.E)
            tk.Label(control_frame, text=angle_title, anchor=tk.W).grid(row=row, column=0, sticky=tk.W, padx=2)
            tk.Scale(control_frame, variable=var, from_=-180, to=180, resolution=0.1, orient=tk.HORIZONTAL,
                     showvalue=False, width=10, sliderlength=15, borderwidth=1
                     ).grid(row=row, column=1, sticky=tk.EW, padx=2)
            var.trace_add("write", lambda *_, v=var, lbl=value_label: lbl.config(text=f"{round(v.get(), 1) + 0.0:.1f}°"))
            value_label.grid(row=row, column=2, padx=2)
            self.scale_vars[name] = var

        # 3. Πλαίσιο με τις τρέχουσες τιμές Roll / Pitch / Yaw κάτω από τον canvas
        # (pack πριν τον canvas, ώστε να μένει ορατό όταν μικραίνει το παράθυρο)
        info_frame = tk.Frame(gyro_tab, relief=tk.SUNKEN, borderwidth=2)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        self.angle_vars = {}
        for name, title in self.angle_titles.items():
            var = tk.StringVar(value=f"{title}: ---")
            tk.Label(info_frame, textvariable=var, width=12, anchor=tk.W,
                     font="TkDefaultFont").pack(side=tk.LEFT, expand=True, padx=2, pady=1)
            self.angle_vars[name] = var

        shape_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.view_size = (CANVAS_WIDTH, CANVAS_HEIGHT)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.canvas_image_id = self.canvas.create_image(0, 0, anchor=tk.NW)
        self.tk_image = None

        # 5. Tab Compass: από κάτω προς τα πάνω (pack με side=BOTTOM) το πλαίσιο με τον
        # slider, το info_frame, και από πάνω το compass_frame με τον canvas
        # Slider North: τιμή χωρίς Sense HAT, αλλιώς offset στο sense.get_compass()
        compass_control = tk.Frame(compass_tab, relief=tk.SUNKEN, borderwidth=2)
        compass_control.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        compass_control.columnconfigure(1, weight=1)
        title = "Compass value" if self.sense is None else "Compass offset"
        tk.Label(compass_control, text=title, font="TkDefaultFont 9 bold").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=2)
        # Πηγή του North: Raw = από τα raw X/Y του μαγνητόμετρου (πλακέτα οριζόντια),
        # get_compass() = από το fusion του RTIMULib (θέλει calibration με RTIMULibCal)
        self.compass_source = tk.StringVar(value="raw")
        source_frame = tk.Frame(compass_control)
        source_frame.grid(row=0, column=1, columnspan=2, sticky=tk.E, padx=2)
        for text, value in (("Raw XY", "raw"), ("sense compass", "fusion")):
            tk.Radiobutton(source_frame, text=text, value=value, variable=self.compass_source,
                           padx=0, pady=0, borderwidth=0, highlightthickness=0,
                           state=tk.DISABLED if self.sense is None else tk.NORMAL
                           ).pack(side=tk.LEFT, padx=(6, 0))
        self.north_var = tk.DoubleVar(value=0.0)
        north_label = tk.Label(compass_control, text="0.0°", width=7, anchor=tk.E)
        tk.Label(compass_control, text="North", anchor=tk.W).grid(row=1, column=0, sticky=tk.W, padx=2)
        tk.Scale(compass_control, variable=self.north_var, from_=-180, to=180, resolution=0.1,
                 orient=tk.HORIZONTAL, showvalue=False, width=10, sliderlength=15, borderwidth=1
                 ).grid(row=1, column=1, sticky=tk.EW, padx=2)
        self.north_var.trace_add("write", lambda *_: north_label.config(
            text=f"{round(self.north_var.get(), 1) + 0.0:.1f}°"))
        north_label.grid(row=1, column=2, padx=2)

        compass_info = tk.Frame(compass_tab, relief=tk.SUNKEN, borderwidth=2)
        compass_info.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        # Γραμμή 1: North + raw X/Y/Z. Γραμμή 2 (διάγνωση): ένταση πεδίου και
        # heading υπολογισμένο απευθείας από τα raw X/Y (χωρίς το fusion του RTIMULib)
        self.compass_vars = {}
        self.compass_label_widgets = {}
        for names in (("north", "x", "y", "z"), ("field", "raw_heading")):
            row = tk.Frame(compass_info)
            row.pack(fill=tk.X)
            for name in names:
                var = tk.StringVar()
                label = tk.Label(row, textvariable=var, anchor=tk.W, font="TkDefaultFont")
                label.pack(side=tk.LEFT, padx=(4, 6), pady=0)
                self.compass_vars[name] = var
                self.compass_label_widgets[name] = label
        self._show_compass_values(None, None)
        self.compass_ticks = 0
        # compass_frame: αριστερά το tool frame με τα κουμπιά (όπως στο Gyroscope), δεξιά ο canvas
        compass_frame = tk.Frame(compass_tab)
        compass_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        compass_tools = tk.Frame(compass_frame)
        compass_tools.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        self.compass_buttons = {}
        # H = hard-iron calibration του μαγνητόμετρου (πάτημα: έναρξη, περιστροφή, πάτημα: αποθήκευση)
        compass_commands = {"H": self.toggle_hard_iron, "S": None}
        for text, command in compass_commands.items():
            button = tk.Button(compass_tools, text=text, width=2, height=2, padx=0, pady=0, command=command)
            button.pack(side=tk.TOP, pady=(10, 0))
            self.compass_buttons[text] = button
        # Hard-iron calibration του μαγνητόμετρου (module compass, φορτώνει τα αποθηκευμένα offsets).
        # Χωρίς Sense HAT δεν υπάρχει αισθητήρας για calibration, οπότε το H είναι ανενεργό
        self.hard_iron = compass.HardIronCalibration()
        self.button_bg = self.compass_buttons["H"].cget("bg")
        if self.sense is None:
            self.compass_buttons["H"].config(state=tk.DISABLED)
        # Σχεδίαση της πυξίδας από το module compass
        self.compass_canvas = tk.Canvas(compass_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.compass_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.compass_view = compass.CompassView(self.compass_canvas)

        # 6. Tabs Magnetometer και Accelerometer: ίδιο design (βλ. _build_vector_tab)
        self.magnet = self._build_vector_tab(magnet_tab, "Magnetometer", "µT", MAGNET_RANGE, 0.1, 1)
        self._show_magnet_values(None)
        self.accel = self._build_vector_tab(accel_tab, "Accelerometer", "g", ACCEL_RANGE, 0.01, 2,
                                            range_choices=ACCEL_RANGE_CHOICES)
        self._show_accel_values(None)

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.render_loop()
        self.compass_loop()
        self.magnet_loop()
        self.accel_loop()

    def calibrate(self):
        # Offset = η αντίστροφη περιστροφή της τρέχουσας θέσης του αισθητήρα, ώστε
        # Roll, Pitch, Yaw του σχήματος = 0, 0, 0 και οι επόμενες κινήσεις να
        # μετριούνται σχετικά με αυτή τη θέση (σωστά και όταν η πλακέτα είναι γερμένη)
        if self.sense is None:
            self.reset_offsets()
            return
        if self.sensor is None:
            self.sensor = self.sense.get_orientation()
        offsets = matrix_to_euler(euler_to_matrix(self.sensor).T)
        for name, var in self.scale_vars.items():
            var.set(offsets[name])

    def reset_offsets(self):
        # Offsets = 0: το σχήμα ακολουθεί ξανά ακριβώς τον αισθητήρα
        for var in self.scale_vars.values():
            var.set(0.0)

    def _on_canvas_resize(self, event):
        self.view_size = (max(event.width, 1), max(event.height, 1))

    def close(self):
        self.scene.close()
        self.root.destroy()

    def _selected_tab(self):
        return self.notebook.nametowidget(self.notebook.select())

    def _on_tab_changed(self, event):
        # Αισθητήρες του IMU ανά tab: set_imu_config(compass, gyroscope, accelerometer)
        # Compass, Magnetometer: μόνο μαγνητόμετρο (όπως το κάνει και το sense.get_compass())
        # Accelerometer: μόνο επιταχυνσιόμετρο
        # Gyroscope: όλοι οι αισθητήρες (gyroscope + accelerometer + μαγνητόμετρο)
        if self.sense is None:
            return
        tab = self._selected_tab()
        if tab is self.compass_tab or tab is self.magnet_tab:
            self.sense.set_imu_config(True, False, False)
        elif tab is self.accel_tab:
            self.sense.set_imu_config(False, False, True)
        elif tab is self.gyro_tab:
            self.sense.set_imu_config(True, True, True)

    def render_loop(self):
        # Σχεδιάζει μόνο όταν φαίνεται το tab Gyroscope (λιγότερη CPU, και δεν
        # διαβάζει get_orientation() όσο το Compass έχει το IMU σε compass-only)
        if self._selected_tab() is self.gyro_tab:
            if not self._render_gyro():
                return
        self.root.after(15, self.render_loop)

    def compass_loop(self):
        # Χωρίς Sense HAT ο slider δίνει την τιμή North, αλλιώς προστίθεται ως offset.
        # Ανάγνωση κάθε 20 ms (το fusion του RTIMULib συγκλίνει με κάθε ανάγνωση),
        # αλλά ενημέρωση οθόνης κάθε 2η φορά (40 ms) για λιγότερη CPU
        if self._selected_tab() is self.compass_tab:
            north = self.north_var.get()
            raw = None
            if self.sense is not None:
                raw = self._read_magnet()
                if self.compass_source.get() == "raw":
                    north += compass.raw_heading(raw)
                else:
                    north += self.sense.get_compass()
            self.compass_view.heading = north % 360.0
            self.compass_ticks += 1
            if self.compass_ticks % 2 == 0:
                self._show_compass_values(self.compass_view.heading, raw)
                self.compass_view.draw()
        self.root.after(20, self.compass_loop)

    def _show_compass_values(self, heading, raw):
        self.compass_vars["north"].set("North: ---" if heading is None else f"North: {round(heading, 1) % 360.0:.1f}°")
        for axis in ("x", "y", "z"):
            value = "---" if raw is None else f"{raw[axis]:.1f} µT"
            self.compass_vars[axis].set(f"{axis.upper()}: {value}")
        # Διάγνωση: η ένταση του γήινου πεδίου είναι ~25-65 µT και μένει σταθερή όταν
        # η πλακέτα περιστρέφεται· το raw heading ισχύει μόνο με την πλακέτα οριζόντια
        xy_angle = "---" if raw is None else f"{compass.xy_angle(raw):.1f}°"
        self._show_field(self.compass_vars["field"], self.compass_label_widgets["field"], "Field |B|", raw)
        self.compass_vars["raw_heading"].set(f"Raw XY heading: {xy_angle}")

    def _read_magnet(self):
        # Ανάγνωση του μαγνητόμετρου (µT) διορθωμένη με τα hard-iron offsets (module compass)
        return self.hard_iron.correct(self.sense.get_compass_raw())

    def toggle_hard_iron(self):
        # Κουμπί H: 1ο πάτημα έναρξη καταγραφής (περιστροφή της πλακέτας σε πλήρη κύκλο),
        # 2ο πάτημα υπολογισμός και αποθήκευση των offsets (βλ. compass.HardIronCalibration)
        button = self.compass_buttons["H"]
        if not self.hard_iron.recording:
            self.hard_iron.start()
            button.config(relief=tk.SUNKEN, bg="orange")
            return
        updated = self.hard_iron.stop()
        button.config(relief=tk.RAISED, bg=self.button_bg)
        if not updated:
            messagebox.showwarning("Hard-iron calibration",
                                   "Not enough rotation, the previous calibration is kept.\n"
                                   "Turn the board slowly through a full circle while recording.")
            return
        kept = [axis.upper() for axis in ("x", "y", "z") if axis not in updated]
        offsets = ", ".join(f"{axis.upper()}: {self.hard_iron.offsets[axis]:.1f} µT" for axis in ("x", "y", "z"))
        messagebox.showinfo("Hard-iron calibration",
                            f"Offsets: {offsets}" + (f"\nKept previous: {', '.join(kept)} (small range)" if kept else ""))

    def _build_vector_tab(self, tab, title, unit, value_range, resolution, decimals, range_choices=None):
        # Κοινό design για Magnetometer και Accelerometer: από κάτω προς τα πάνω (pack με
        # side=BOTTOM) οι sliders προσομοίωσης (μόνο χωρίς Sense HAT), το info_frame,
        # η επιλογή κλίμακας (αν δοθεί range_choices), και το frame με τους δύο canvas:
        # X/Y σε σταυρό και Z σε στενότερο canvas
        panel = {"unit": unit, "decimals": decimals, "vars": {}, "labels": {}, "label_widgets": {}}
        if self.sense is None:
            control = tk.Frame(tab, relief=tk.SUNKEN, borderwidth=2)
            control.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
            control.columnconfigure(1, weight=1)
            tk.Label(control, text=f"{title} values", font="TkDefaultFont 9 bold").grid(
                row=0, column=0, columnspan=3, sticky=tk.W, padx=2)
            for row, axis in enumerate(("x", "y", "z"), start=1):
                var = tk.DoubleVar(value=0.0)
                value_label = tk.Label(control, text=f"{0:.{decimals}f} {unit}", width=9, anchor=tk.E)
                tk.Label(control, text=axis.upper(), anchor=tk.W).grid(row=row, column=0, sticky=tk.W, padx=2)
                tk.Scale(control, variable=var, from_=-value_range, to=value_range, resolution=resolution,
                         orient=tk.HORIZONTAL, showvalue=False, width=10, sliderlength=15, borderwidth=1
                         ).grid(row=row, column=1, sticky=tk.EW, padx=2)
                var.trace_add("write", lambda *_, v=var, lbl=value_label: lbl.config(
                    text=f"{round(v.get(), decimals) + 0.0:.{decimals}f} {unit}"))
                value_label.grid(row=row, column=2, padx=2)
                panel["vars"][axis] = var

        info = tk.Frame(tab, relief=tk.SUNKEN, borderwidth=2)
        info.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        for name in ("x", "y", "z", "total"):
            var = tk.StringVar()
            label = tk.Label(info, textvariable=var, anchor=tk.W, font="TkDefaultFont")
            label.pack(side=tk.LEFT, padx=(4, 6), pady=0)
            panel["labels"][name] = var
            panel["label_widgets"][name] = label

        if range_choices:
            # Μέγιστη τιμή στο άκρο των αξόνων, ξεχωριστά για τον σταυρό X/Y και τον Z
            range_frame = tk.Frame(tab, relief=tk.SUNKEN, borderwidth=2)
            range_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
            tk.Label(range_frame, text="Axes range", font="TkDefaultFont 9 bold").pack(side=tk.LEFT, padx=(4, 8))
            for key, text in (("range_xy", "X/Y:"), ("range_z", "Z:")):
                values, default = range_choices[key]
                tk.Label(range_frame, text=text).pack(side=tk.LEFT, padx=(4, 2))
                choice = ttk.Combobox(range_frame, values=[f"{v:g}" for v in values],
                                      width=4, state="readonly")
                choice.set(f"{default:g}")
                choice.pack(side=tk.LEFT, pady=1)
                tk.Label(range_frame, text=unit).pack(side=tk.LEFT, padx=(2, 6))

                def on_select(event, key=key, choice=choice):
                    setattr(panel["view"], key, float(choice.get()))
                    panel["view"].draw()
                choice.bind("<<ComboboxSelected>>", on_select)

        frame = tk.Frame(tab)
        frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        # Οι δύο canvas (X/Y και Z) από το module xyz_force
        panel["view"] = xyz_force.XYZForceView(frame, value_range, size=CANVAS_HEIGHT)
        if range_choices:
            for key, (values, default) in range_choices.items():
                setattr(panel["view"], key, default)
        return panel

    def magnet_loop(self):
        # Raw μαγνητόμετρο (Sense HAT, με hard-iron διόρθωση) ή οι sliders, κάθε 50 ms
        if self._selected_tab() is self.magnet_tab:
            if self.sense is not None:
                raw = self._read_magnet()
            else:
                raw = {axis: var.get() for axis, var in self.magnet["vars"].items()}
            self._show_magnet_values(raw)
            self.magnet["view"].draw(raw)
        self.root.after(50, self.magnet_loop)

    def accel_loop(self):
        # Raw επιταχυνσιόμετρο σε g (Sense HAT) ή οι sliders, κάθε 50 ms
        if self._selected_tab() is self.accel_tab:
            if self.sense is not None:
                raw = self.sense.get_accelerometer_raw()
            else:
                raw = {axis: var.get() for axis, var in self.accel["vars"].items()}
            self._show_accel_values(raw)
            self.accel["view"].draw(raw)
        self.root.after(50, self.accel_loop)

    @staticmethod
    def _show_axis_values(panel, raw):
        for axis in ("x", "y", "z"):
            value = "---" if raw is None else f"{raw[axis]:.{panel['decimals']}f} {panel['unit']}"
            panel["labels"][axis].set(f"{axis.upper()}: {value}")

    def _show_magnet_values(self, raw):
        self._show_axis_values(self.magnet, raw)
        self._show_field(self.magnet["labels"]["total"], self.magnet["label_widgets"]["total"], "|B|", raw)

    def _show_accel_values(self, raw):
        # |a| ≈ 1 g σε ηρεμία (μόνο η βαρύτητα), σε όποια θέση κι αν είναι η πλακέτα
        self._show_axis_values(self.accel, raw)
        total = "---" if raw is None else f"{xyz_force.magnitude(raw):.2f} g"
        self.accel["labels"]["total"].set(f"|a|: {total}")

    @staticmethod
    def _show_field(var, label, title, raw):
        # Ένταση πεδίου |B| με προειδοποίηση όταν ένας μαγνήτης είναι πολύ κοντά:
        # πορτοκαλί πάνω από FIELD_WARN, κόκκινο με "too close!" πάνω από FIELD_DANGER
        # (εκεί κοντινά ατσάλινα μέρη μπορεί να μαγνητιστούν -> νέο hard-iron offset)
        if raw is None:
            var.set(f"{title}: ---")
            label.config(fg="black")
            return
        field = xyz_force.magnitude(raw)
        if field > FIELD_DANGER:
            var.set(f"{title}: {field:.1f} µT  too close!")
            label.config(fg="red")
        else:
            var.set(f"{title}: {field:.1f} µT")
            label.config(fg=FIELD_WARN_COLOR if field > FIELD_WARN else "black")

    def _render_gyro(self):
        # Χωρίς Sense HAT οι sliders δίνουν τις τιμές, αλλιώς είναι μια περιστροφή
        # offset που εφαρμόζεται πριν από αυτή του αισθητήρα: R = R_offset · R_sensor
        orientation = {name: var.get() for name, var in self.scale_vars.items()}
        if self.sense is not None:
            self.sensor = self.sense.get_orientation()
            orientation = matrix_to_euler(euler_to_matrix(orientation) @ euler_to_matrix(self.sensor))

        image = self.scene.render(orientation, self.view_size)
        if image is None:  # η 3D σκηνή έκλεισε
            self.close()
            return False

        for name, var in self.angle_vars.items():
            var.set(f"{self.angle_titles[name]}: {round(orientation[name], 1) + 0.0:4.1f}°")
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(image))
        self.canvas.itemconfig(self.canvas_image_id, image=self.tk_image)
        return True

if __name__ == "__main__":
    window = tk.Tk()
    app = Transparent3DCubeApp(window)
    window.mainloop()
