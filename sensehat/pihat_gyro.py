import json
import math
import os
import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
from PIL import Image, ImageTk

# Module της 3D σκηνής: για άλλη 3D βιβλιοθήκη αλλάζει μόνο αυτό το import
# (το module πρέπει να δίνει GyroScene με το ίδιο interface, βλ. pi3d_gyro.py)
import pi3d_gyro as gyro3d

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


def raw_heading(raw):
    # Heading (0..360, αυξάνει δεξιόστροφα όπως η πυξίδα) από τα raw X/Y του
    # μαγνητόμετρου. Η γωνία atan2(y, x) μικραίνει όταν η πλακέτα στρίβει δεξιόστροφα,
    # γι' αυτό 360 - γωνία. Σωστό μόνο με την πλακέτα οριζόντια.
    return (360.0 - math.degrees(math.atan2(raw["y"], raw["x"]))) % 360.0


WINDOW_TITLE = "Sense Gyroscope"

CANVAS_BG_COLOR = "light gray"
CANVAS_WIDTH = 350
CANVAS_HEIGHT = 250
COMPASS_BG_COLOR = "#1a1a1a"  # ίδιο με το φόντο της 3D σκηνής
MAGNET_RANGE = 100.0  # µT στο άκρο των αξόνων (γήινο πεδίο ~25-65 µT)
ACCEL_RANGE = 2.0  # g στο άκρο των αξόνων (σε ηρεμία |a| ≈ 1 g, η βαρύτητα)

# Hard-iron calibration: αρχείο με τα offsets (µT) δίπλα στο script, και ελάχιστο
# εύρος τιμών ανά άξονα στην καταγραφή για να θεωρηθεί ο άξονας βαθμονομημένος
HARD_IRON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pihat_gyro_hardiron.json")
HARD_IRON_MIN_SPAN = 20.0

# Προειδοποίηση έντασης πεδίου (µT) για πειράματα με μαγνήτη
FIELD_WARN = 150.0
FIELD_DANGER = 300.0
FIELD_WARN_COLOR = "#d07000"  # σκούρο πορτοκαλί, ευανάγνωστο σε ανοιχτό φόντο


def load_hard_iron():
    try:
        with open(HARD_IRON_FILE) as f:
            data = json.load(f)
        return {axis: float(data[axis]) for axis in ("x", "y", "z")}
    except (OSError, ValueError, KeyError, TypeError):
        return {"x": 0.0, "y": 0.0, "z": 0.0}


def save_hard_iron(offsets):
    with open(HARD_IRON_FILE, "w") as f:
        json.dump(offsets, f, indent=2)

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
        self.heading = None  # τελική τιμή North (αισθητήρας + offset, ή ο slider)
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
        # Hard-iron offsets (µT) που αφαιρούνται από κάθε ανάγνωση του μαγνητόμετρου.
        # Χωρίς Sense HAT δεν υπάρχει αισθητήρας για calibration, οπότε το H είναι ανενεργό
        self.hard_iron = load_hard_iron()
        self.hard_iron_rec = None  # min/max ανά άξονα όσο γίνεται η καταγραφή
        self.button_bg = self.compass_buttons["H"].cget("bg")
        if self.sense is None:
            self.compass_buttons["H"].config(state=tk.DISABLED)
        self.compass_canvas = tk.Canvas(compass_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                                        bg=COMPASS_BG_COLOR, highlightthickness=0)
        self.compass_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.compass_canvas.bind("<Configure>", lambda event: self._draw_compass())

        # 6. Tabs Magnetometer και Accelerometer: ίδιο design (βλ. _build_vector_tab)
        self.magnet = self._build_vector_tab(magnet_tab, "Magnetometer", "µT", MAGNET_RANGE, 0.1, 1)
        self._show_magnet_values(None)
        self.accel = self._build_vector_tab(accel_tab, "Accelerometer", "g", ACCEL_RANGE, 0.01, 2)
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
                    north += raw_heading(raw)
                else:
                    north += self.sense.get_compass()
            self.heading = north % 360.0
            self.compass_ticks += 1
            if self.compass_ticks % 2 == 0:
                self._show_compass_values(self.heading, raw)
                self._draw_compass()
        self.root.after(20, self.compass_loop)

    def _show_compass_values(self, heading, raw):
        self.compass_vars["north"].set("North: ---" if heading is None else f"North: {round(heading, 1) % 360.0:.1f}°")
        for axis in ("x", "y", "z"):
            value = "---" if raw is None else f"{raw[axis]:.1f} µT"
            self.compass_vars[axis].set(f"{axis.upper()}: {value}")
        # Διάγνωση: η ένταση του γήινου πεδίου είναι ~25-65 µT και μένει σταθερή όταν
        # η πλακέτα περιστρέφεται· το raw heading ισχύει μόνο με την πλακέτα οριζόντια
        xy_angle = "---" if raw is None else f"{math.degrees(math.atan2(raw['y'], raw['x'])) % 360.0:.1f}°"
        self._show_field(self.compass_vars["field"], self.compass_label_widgets["field"], "Field |B|", raw)
        self.compass_vars["raw_heading"].set(f"Raw XY heading: {xy_angle}")

    def _draw_compass(self):
        # Πυξίδα: η ροδέλα στρέφεται ώστε το N να δείχνει τον πραγματικό βορρά,
        # το κίτρινο τρίγωνο πάνω είναι η κατεύθυνση της πλακέτας
        c = self.compass_canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        cx, cy = w / 2.0, h / 2.0
        r = min(w, h) / 2.0 - 14
        if r < 20:
            return
        rotation = -(self.heading or 0.0)

        def point(angle, radius):
            a = math.radians(angle + rotation)
            return cx + radius * math.sin(a), cy - radius * math.cos(a)

        c.create_oval(cx - r, cy - r, cx + r, cy + r, outline="white", width=2)
        for deg in range(0, 360, 10):
            length = 12 if deg % 30 == 0 else 6
            c.create_line(*point(deg, r), *point(deg, r - length), fill="white")
        for deg, text in ((0, "N"), (90, "E"), (180, "S"), (270, "W")):
            c.create_text(*point(deg, r - 26), text=text, fill="red" if text == "N" else "white",
                          font="TkDefaultFont 12 bold")
        # Βελόνα: κόκκινο προς Βορρά, γκρι προς Νότο
        needle = r - 42
        c.create_polygon(*point(0, needle), *point(90, 6), *point(270, 6), fill="red", outline="")
        c.create_polygon(*point(180, needle), *point(90, 6), *point(270, 6), fill="gray60", outline="")
        c.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="white", outline="")
        # Σταθερό σημάδι της κατεύθυνσης της πλακέτας
        c.create_polygon(cx, cy - r + 2, cx - 7, cy - r - 12, cx + 7, cy - r - 12, fill="yellow", outline="")

    def _read_magnet(self):
        # Ανάγνωση του μαγνητόμετρου (µT) διορθωμένη με τα hard-iron offsets.
        # Όσο γίνεται καταγραφή (H), κρατάει min/max των αδιόρθωτων τιμών.
        raw = self.sense.get_compass_raw()
        if self.hard_iron_rec is not None:
            for axis, (low, high) in self.hard_iron_rec.items():
                self.hard_iron_rec[axis] = (min(low, raw[axis]), max(high, raw[axis]))
        return {axis: raw[axis] - self.hard_iron[axis] for axis in ("x", "y", "z")}

    def toggle_hard_iron(self):
        # 1ο πάτημα: έναρξη καταγραφής -> περιστροφή της πλακέτας σε πλήρη κύκλο
        # (ιδανικά και με κλίσεις). 2ο πάτημα: offset = κέντρο (min+max)/2 ανά άξονα.
        # Άξονες με μικρό εύρος (π.χ. Z όταν η πλακέτα έμεινε οριζόντια) κρατούν το παλιό offset.
        button = self.compass_buttons["H"]
        if self.hard_iron_rec is None:
            self.hard_iron_rec = {axis: (math.inf, -math.inf) for axis in ("x", "y", "z")}
            button.config(relief=tk.SUNKEN, bg="orange")
            return
        record, self.hard_iron_rec = self.hard_iron_rec, None
        button.config(relief=tk.RAISED, bg=self.button_bg)
        updated = [axis for axis, (low, high) in record.items() if high - low >= HARD_IRON_MIN_SPAN]
        if not updated:
            messagebox.showwarning("Hard-iron calibration",
                                   "Not enough rotation, the previous calibration is kept.\n"
                                   "Turn the board slowly through a full circle while recording.")
            return
        for axis in updated:
            low, high = record[axis]
            self.hard_iron[axis] = (low + high) / 2.0
        save_hard_iron(self.hard_iron)
        kept = [axis.upper() for axis in ("x", "y", "z") if axis not in updated]
        offsets = ", ".join(f"{axis.upper()}: {self.hard_iron[axis]:.1f} µT" for axis in ("x", "y", "z"))
        messagebox.showinfo("Hard-iron calibration",
                            f"Offsets: {offsets}" + (f"\nKept previous: {', '.join(kept)} (small range)" if kept else ""))

    def _build_vector_tab(self, tab, title, unit, value_range, resolution, decimals):
        # Κοινό design για Magnetometer και Accelerometer: από κάτω προς τα πάνω (pack με
        # side=BOTTOM) οι sliders προσομοίωσης (μόνο χωρίς Sense HAT), το info_frame, και
        # το frame με τους δύο canvas: X/Y σε σταυρό και Z σε στενότερο canvas
        panel = {"range": value_range, "unit": unit, "decimals": decimals,
                 "vars": {}, "labels": {}, "label_widgets": {}, "raw": None}
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

        frame = tk.Frame(tab)
        frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        panel["xy"] = tk.Canvas(frame, width=CANVAS_HEIGHT, height=CANVAS_HEIGHT,
                                bg=COMPASS_BG_COLOR, highlightthickness=0)
        panel["xy"].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        panel["z"] = tk.Canvas(frame, width=80, height=CANVAS_HEIGHT,
                               bg=COMPASS_BG_COLOR, highlightthickness=0)
        panel["z"].pack(side=tk.LEFT, fill=tk.Y, padx=(2, 0))
        for canvas in (panel["xy"], panel["z"]):
            canvas.bind("<Configure>", lambda event: self._draw_vector(panel))
        return panel

    def magnet_loop(self):
        # Raw μαγνητόμετρο (Sense HAT, με hard-iron διόρθωση) ή οι sliders, κάθε 50 ms
        if self._selected_tab() is self.magnet_tab:
            if self.sense is not None:
                self.magnet["raw"] = self._read_magnet()
            else:
                self.magnet["raw"] = {axis: var.get() for axis, var in self.magnet["vars"].items()}
            self._show_magnet_values(self.magnet["raw"])
            self._draw_vector(self.magnet)
        self.root.after(50, self.magnet_loop)

    def accel_loop(self):
        # Raw επιταχυνσιόμετρο σε g (Sense HAT) ή οι sliders, κάθε 50 ms
        if self._selected_tab() is self.accel_tab:
            if self.sense is not None:
                self.accel["raw"] = self.sense.get_accelerometer_raw()
            else:
                self.accel["raw"] = {axis: var.get() for axis, var in self.accel["vars"].items()}
            self._show_accel_values(self.accel["raw"])
            self._draw_vector(self.accel)
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
        total = "---" if raw is None else f"{math.sqrt(raw['x'] ** 2 + raw['y'] ** 2 + raw['z'] ** 2):.2f} g"
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
        field = math.sqrt(raw["x"] ** 2 + raw["y"] ** 2 + raw["z"] ** 2)
        if field > FIELD_DANGER:
            var.set(f"{title}: {field:.1f} µT  too close!")
            label.config(fg="red")
        else:
            var.set(f"{title}: {field:.1f} µT")
            label.config(fg=FIELD_WARN_COLOR if field > FIELD_WARN else "black")

    @staticmethod
    def _draw_vector(panel):
        # Βέλη με μήκος ανάλογο της τιμής: X οριζόντια (δεξιά +), Y κάθετα (πάνω +),
        # Z κάθετα στον δεύτερο canvas. Ίδια κλίμακα (range στο άκρο) και στους δύο,
        # γραμμές κλίμακας ανά range/4 (μεγαλύτερες ανά range/2)
        raw, value_range = panel["raw"], panel["range"]
        xy, zc = panel["xy"], panel["z"]
        w, h = xy.winfo_width(), xy.winfo_height()
        zw = zc.winfo_width()
        margin = 22
        scale = (min(w, h) / 2.0 - margin) / value_range
        if scale <= 0:
            return
        clamp = lambda v: max(-value_range, min(value_range, v))
        step = value_range / 4.0
        ticks = [(i * step, 5 if i % 2 == 0 else 3) for i in range(-4, 5) if i]

        # Canvas 1: σταυρός X/Y
        xy.delete("all")
        cx, cy = w / 2.0, h / 2.0
        reach = value_range * scale
        xy.create_line(cx - reach, cy, cx + reach, cy, fill="gray50")
        xy.create_line(cx, cy - reach, cx, cy + reach, fill="gray50")
        for t, size in ticks:
            xy.create_line(cx + t * scale, cy - size, cx + t * scale, cy + size, fill="gray50")
            xy.create_line(cx - size, cy - t * scale, cx + size, cy - t * scale, fill="gray50")
        xy.create_text(cx + reach + 10, cy, text="X", fill="red", font="TkDefaultFont 10 bold")
        xy.create_text(cx, cy - reach - 10, text="Y", fill="#00c000", font="TkDefaultFont 10 bold")
        xy.create_text(cx + value_range / 2.0 * scale, cy + 12, text=f"{value_range / 2.0:g}",
                       fill="gray60", font="TkDefaultFont 7")
        if raw is not None:
            xy.create_line(cx, cy, cx + clamp(raw["x"]) * scale, cy, fill="red", width=4,
                           arrow=tk.LAST, arrowshape=(10, 12, 5))
            xy.create_line(cx, cy, cx, cy - clamp(raw["y"]) * scale, fill="#00c000", width=4,
                           arrow=tk.LAST, arrowshape=(10, 12, 5))

        # Canvas 2: οριζόντια γραμμή μηδέν του Z, βέλος πάνω (+) ή κάτω (-)
        zc.delete("all")
        zx, zy = zw / 2.0, zc.winfo_height() / 2.0
        zc.create_line(4, zy, zw - 4, zy, fill="gray50")
        zc.create_line(zx, zy - reach, zx, zy + reach, fill="gray30", dash=(2, 3))
        for t, size in ticks:
            zc.create_line(zx - size, zy - t * scale, zx + size, zy - t * scale, fill="gray50")
        zc.create_text(zx, zy - reach - 10, text="Z", fill="#4080ff", font="TkDefaultFont 10 bold")
        if raw is not None:
            zc.create_line(zx, zy, zx, zy - clamp(raw["z"]) * scale, fill="#4080ff", width=4,
                           arrow=tk.LAST, arrowshape=(10, 12, 5))

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
