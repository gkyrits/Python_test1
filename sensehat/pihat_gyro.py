import math
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk
import numpy as np
from PIL import Image, ImageTk

# Module της 3D σκηνής: για άλλη 3D βιβλιοθήκη αλλάζει μόνο αυτό το import
# (το module πρέπει να δίνει GyroScene με το ίδιο interface, βλ. pi3d_gyro.py)
import pi3d_gyro as gyro3d

# Σχεδίαση πυξίδας (Compass) και διανυσμάτων X/Y/Z (Magnetometer, Accelerometer) σε Tk Canvas
import compass
import xyz_force
import acceleration
import track

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
                       "range_z": ((0.1, 0.5, 1.0, 1.5, 2.0), 1.0)}

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
        # Έντονη εκδοχή της γραμματοσειράς του GUI (για τις προειδοποιήσεις |B|)
        self.bold_font = tkfont.nametofont("TkDefaultFont").copy()
        self.bold_font.configure(weight="bold")

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
        track_tab = tk.Frame(notebook)
        notebook.add(track_tab, text="Track")
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.notebook, self.gyro_tab, self.compass_tab = notebook, gyro_tab, compass_tab
        self.magnet_tab, self.accel_tab, self.track_tab = magnet_tab, accel_tab, track_tab

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
        # Compass offset ανά πηγή (module compass), από το αρχείο που αποθηκεύει το κουμπί S
        self.compass_offsets = compass.CompassOffsets()
        source_frame = tk.Frame(compass_control)
        source_frame.grid(row=0, column=1, columnspan=2, sticky=tk.E, padx=2)
        for text, value in (("Raw XY", "raw"), ("sense compass", "fusion")):
            tk.Radiobutton(source_frame, text=text, value=value, variable=self.compass_source,
                           command=self._on_compass_source,
                           padx=0, pady=0, borderwidth=0, highlightthickness=0,
                           state=tk.DISABLED if self.sense is None else tk.NORMAL
                           ).pack(side=tk.LEFT, padx=(6, 0))
        # Με Sense HAT ο slider είναι το offset της επιλεγμένης πηγής, χωρίς Sense HAT η τιμή North
        self.north_var = tk.DoubleVar(value=0.0 if self.sense is None else self.compass_offsets.values["raw"])
        north_label = tk.Label(compass_control, text="0.0°", width=7, anchor=tk.E)
        tk.Label(compass_control, text="North", anchor=tk.W).grid(row=1, column=0, sticky=tk.W, padx=2)
        tk.Scale(compass_control, variable=self.north_var, from_=-180, to=180, resolution=0.1,
                 orient=tk.HORIZONTAL, showvalue=False, width=10, sliderlength=15, borderwidth=1
                 ).grid(row=1, column=1, sticky=tk.EW, padx=2)
        self.north_var.trace_add("write", lambda *_: north_label.config(
            text=f"{round(self.north_var.get(), 1) + 0.0:.1f}°"))
        self.north_var.trace_add("write", lambda *_: self._on_compass_offset())
        north_label.config(text=f"{round(self.north_var.get(), 1) + 0.0:.1f}°")
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
        # S = αποθήκευση των Compass offsets (Raw XY και sense compass)
        compass_commands = {"H": self.toggle_hard_iron, "S": self.save_compass_offsets}
        for text, command in compass_commands.items():
            button = tk.Button(compass_tools, text=text, width=2, height=2, padx=0, pady=0, command=command)
            button.pack(side=tk.TOP, pady=(10, 0))
            self.compass_buttons[text] = button
        # Hard-iron calibration του μαγνητόμετρου (module compass, φορτώνει τα αποθηκευμένα offsets).
        # Χωρίς Sense HAT δεν υπάρχει αισθητήρας για calibration, οπότε το H είναι ανενεργό
        self.hard_iron = compass.HardIronCalibration()
        # Αρχικά χρώματα του H (bg, και activebackground που φαίνεται όσο το ποντίκι είναι πάνω του)
        self.button_colors = {key: self.compass_buttons["H"].cget(key) for key in ("bg", "activebackground")}
        if self.sense is None:
            self.compass_buttons["H"].config(state=tk.DISABLED)
            self.compass_buttons["S"].config(state=tk.DISABLED)
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
        # Raw = μέτρηση όπως είναι (με τη βαρύτητα), Linear = χωρίς βαρύτητα σε X, Y, Z
        # (module acceleration, με την κλίση από gyroscope + accelerometer).
        # Χωρίς Sense HAT δεν υπάρχει προσανατολισμός για την αφαίρεση, οπότε μόνο Raw.
        self.accel_mode = tk.StringVar(value="raw" if self.sense is None else "linear")
        mode_frame = tk.Frame(self.accel["options"])
        mode_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(mode_frame, text="Mode", font="TkDefaultFont 9 bold").pack(side=tk.LEFT, padx=(4, 8))
        for text, value in (("Raw", "raw"), ("Linear (gravity removed)", "linear")):
            tk.Radiobutton(mode_frame, text=text, value=value, variable=self.accel_mode,
                           command=self._on_accel_mode,
                           padx=0, pady=0, borderwidth=0, highlightthickness=0,
                           state=tk.DISABLED if self.sense is None else tk.NORMAL
                           ).pack(side=tk.LEFT, padx=(4, 8), pady=1)
        # Διόρθωση υπολοίπου στο Linear (module acceleration): Zero = μέσος όρος ~1 s με την
        # πλακέτα ακίνητη, Auto-zero = αργό φίλτρο που αφαιρεί συνεχώς ό,τι μένει σταθερό
        self.accel_correction = acceleration.ResidualCorrection()
        correction_frame = tk.Frame(self.accel["options"])
        correction_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(correction_frame, text="Residual", font="TkDefaultFont 9 bold").pack(side=tk.LEFT, padx=(4, 8))
        self.zero_button = tk.Button(correction_frame, text="Zero", padx=6, pady=0, command=self.zero_accel)
        self.zero_button.pack(side=tk.LEFT, padx=(4, 8), pady=1)
        self.zero_colors = {key: self.zero_button.cget(key) for key in ("bg", "activebackground")}
        self.auto_zero_var = tk.BooleanVar(value=False)
        self.auto_zero_check = tk.Checkbutton(correction_frame, text="Auto-zero", variable=self.auto_zero_var,
                                              command=self._on_auto_zero, padx=0, pady=0,
                                              borderwidth=0, highlightthickness=0)
        self.auto_zero_check.pack(side=tk.LEFT, padx=(4, 8))
        self._update_correction_controls()

        # 7. Tab Track: από κάτω προς τα πάνω (pack με side=BOTTOM) οι επιλογές, το info_frame,
        # και το frame με τον canvas της διαδρομής (module track: ταχύτητα και διαδρομή από τη
        # γραμμική επιτάχυνση, με ZUPT και διόρθωση drift σε κάθε στάση, σε νήμα)
        self.tracker = track.Tracker()
        # Το Track διαβάζει το μαγνητόμετρο απευθείας (όπως η πηγή Raw XY), οπότε παίρνει εκείνο το offset
        self.tracker.heading_offset = self.compass_offsets.values["raw"] if self.sense is not None else 0.0
        self.track_sampler = track.TrackSampler(self._read_track_sample, self.tracker)
        track_options = tk.Frame(track_tab, relief=tk.SUNKEN, borderwidth=2)
        track_options.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        state = tk.DISABLED if self.sense is None else tk.NORMAL
        buttons_row = tk.Frame(track_options)
        buttons_row.pack(fill=tk.X)
        self.track_button = tk.Button(buttons_row, text="Start", width=6, padx=2, pady=0,
                                      command=self.toggle_track, state=state)
        self.track_button.pack(side=tk.LEFT, padx=(4, 4), pady=1)
        self.track_colors = {key: self.track_button.cget(key) for key in ("bg", "activebackground")}
        tk.Button(buttons_row, text="Reset", width=6, padx=2, pady=0, command=self.reset_track,
                  state=state).pack(side=tk.LEFT, padx=(0, 8), pady=1)
        # Board: άξονες της πλακέτας (πάνω = μπροστά, χωρίς στροφές), Gyro: πάνω = κατεύθυνση στο
        # Start και οι στροφές από το gyroscope, Compass: Βορράς πάνω (μαγνητόμετρο με διόρθωση κλίσης)
        heading_row = tk.Frame(track_options)
        heading_row.pack(fill=tk.X)
        tk.Label(heading_row, text="Heading", font="TkDefaultFont 9 bold").pack(side=tk.LEFT, padx=(4, 4))
        self.track_heading = tk.StringVar(value="board")
        for text, value in (("Board", "board"), ("Gyro", "gyro"), ("Compass", "compass")):
            tk.Radiobutton(heading_row, text=text, value=value, variable=self.track_heading,
                           command=self._on_track_heading, padx=0, pady=0, borderwidth=0,
                           highlightthickness=0, state=state).pack(side=tk.LEFT, padx=(4, 4), pady=1)

        track_info = tk.Frame(track_tab, relief=tk.SUNKEN, borderwidth=2)
        track_info.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        self.track_vars = {}
        self.track_label_widgets = {}
        for name in ("speed", "distance", "position", "state"):
            var = tk.StringVar()
            label = tk.Label(track_info, textvariable=var, anchor=tk.W, font="TkDefaultFont")
            label.pack(side=tk.LEFT, padx=(4, 6), pady=0)
            self.track_vars[name] = var
            self.track_label_widgets[name] = label
        self._show_track_values(self.tracker.snapshot())

        track_frame = tk.Frame(track_tab)
        track_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        track_canvas = tk.Canvas(track_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        track_canvas.pack(fill=tk.BOTH, expand=True)
        self.track_view = track.TrackView(track_canvas)
        if self.sense is None:
            self.track_view.message = "Track needs a Sense HAT"

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.render_loop()
        self.compass_loop()
        self.magnet_loop()
        self.accel_loop()
        self.track_loop()

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
        self.track_sampler.stop()
        self.scene.close()
        self.root.destroy()

    def _selected_tab(self):
        return self.notebook.nametowidget(self.notebook.select())

    def _on_tab_changed(self, event):
        # Αισθητήρες του IMU ανά tab: set_imu_config(compass, gyroscope, accelerometer)
        # Compass, Magnetometer: μόνο μαγνητόμετρο (όπως το κάνει και το sense.get_compass())
        # Accelerometer: μόνο επιταχυνσιόμετρο (Raw), ή gyroscope + accelerometer (Linear,
        #                για τον προσανατολισμό που αφαιρεί τη βαρύτητα)
        # Gyroscope, Track: όλοι οι αισθητήρες (gyroscope + accelerometer + μαγνητόμετρο)
        # Το Track σταματάει όταν φεύγει κανείς από το tab: το νήμα του διαβάζει τον
        # αισθητήρα και δεν πρέπει να τρέχει μαζί με τα loops των άλλων tabs
        if self.sense is None:
            return
        tab = self._selected_tab()
        if tab is not self.track_tab:
            self._stop_track()
        if tab is self.compass_tab or tab is self.magnet_tab:
            self.sense.set_imu_config(True, False, False)
        elif tab is self.accel_tab:
            self.sense.set_imu_config(False, self.accel_mode.get() == "linear", True)
        elif tab is self.gyro_tab or tab is self.track_tab:
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

    def _on_compass_source(self):
        # Αλλαγή πηγής: ο slider δείχνει το offset της νέας πηγής
        self.north_var.set(self.compass_offsets.values[self.compass_source.get()])

    def _on_compass_offset(self):
        # Ο slider άλλαξε: κρατάει το offset της επιλεγμένης πηγής, και το Raw XY πάει και στο Track
        if self.sense is None:
            return
        self.compass_offsets.values[self.compass_source.get()] = self.north_var.get()
        if hasattr(self, "tracker"):
            self.tracker.heading_offset = self.compass_offsets.values["raw"]

    def save_compass_offsets(self):
        # Κουμπί S: αποθήκευση και των δύο offsets, φορτώνονται ξανά στην επόμενη εκκίνηση
        try:
            self.compass_offsets.save()
        except OSError as e:
            messagebox.showerror("Compass offset", f"Could not save: {e}")
            return
        values = self.compass_offsets.values
        messagebox.showinfo("Compass offset", f"Saved: Raw XY {values['raw']:.1f}°, "
                                              f"sense compass {values['fusion']:.1f}°")

    def toggle_hard_iron(self):
        # Κουμπί H: 1ο πάτημα έναρξη καταγραφής (περιστροφή της πλακέτας σε πλήρη κύκλο),
        # 2ο πάτημα υπολογισμός και αποθήκευση των offsets (βλ. compass.HardIronCalibration)
        button = self.compass_buttons["H"]
        if not self.hard_iron.recording:
            self.hard_iron.start()
            button.config(relief=tk.SUNKEN, bg="orange", activebackground="orange")
            return
        updated = self.hard_iron.stop()
        button.config(relief=tk.RAISED, **self.button_colors)
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
        # side=BOTTOM) οι sliders προσομοίωσης (μόνο χωρίς Sense HAT), το πλαίσιο επιλογών
        # (αν δοθεί range_choices), το info_frame, και το frame με τους δύο canvas:
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

        if range_choices:
            # Πλαίσιο επιλογών: γραμμή με τη μέγιστη τιμή στο άκρο των αξόνων, ξεχωριστά
            # για τον σταυρό X/Y και τον Z (επιπλέον γραμμές μπαίνουν στο panel["options"])
            options = tk.Frame(tab, relief=tk.SUNKEN, borderwidth=2)
            options.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
            range_frame = tk.Frame(options)
            range_frame.pack(side=tk.BOTTOM, fill=tk.X)
            panel["options"] = options
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
        panel["frame"] = frame
        # Οι δύο canvas (X/Y και Z) από το module xyz_force
        panel["view"] = xyz_force.XYZForceView(frame, value_range, size=CANVAS_HEIGHT)
        if range_choices:
            for key, (values, default) in range_choices.items():
                setattr(panel["view"], key, default)
        return panel

    def _on_accel_mode(self):
        # Αλλαγή Raw/Linear: νέες ρυθμίσεις IMU, και το υπόλοιπο μετριέται από την αρχή
        self.accel_correction.reset()
        self.zero_button.config(**self.zero_colors)
        self._update_correction_controls()
        self._on_tab_changed(None)

    def _update_correction_controls(self):
        # Zero / Auto-zero έχουν νόημα μόνο στο Linear (και μόνο με Sense HAT)
        state = tk.NORMAL if self.accel_mode.get() == "linear" else tk.DISABLED
        self.zero_button.config(state=state)
        self.auto_zero_check.config(state=state)

    def zero_accel(self):
        # Κουμπί Zero: μέσος όρος ~1 s (πορτοκαλί όσο μετράει), η πλακέτα πρέπει να μένει ακίνητη
        self.accel_correction.start_zero()
        self.zero_button.config(bg="orange", activebackground="orange")

    def _on_auto_zero(self):
        self.accel_correction.auto = self.auto_zero_var.get()

    def _read_track_sample(self):
        # Καλείται από το νήμα του Track: (επιτάχυνση g, προσανατολισμός μοίρες, gyroscope rad/s,
        # μαγνητόμετρο µT με hard-iron διόρθωση ή None, χρόνος s ή None), ή None χωρίς νέο δείγμα.
        # Αν γίνεται, ΜΙΑ ανάγνωση του RTIMULib για όλα (ίδια στιγμή, χρόνος του IMU, πιο
        # γρήγορα), αντί για τρεις ξεχωριστές αναγνώσεις μέσω του sense_hat.
        use_mag = self.tracker.heading_mode in ("gyro", "compass")  # Gyro: αρχική κατεύθυνση από την πυξίδα
        imu = getattr(self.sense, "_imu", None)
        if imu is not None and hasattr(imu, "getIMUData"):
            if not imu.IMURead():
                return None
            data = imu.getIMUData()
            roll, pitch, yaw = (math.degrees(v) for v in data["fusionPose"])
            mag = self.hard_iron.correct(dict(zip("xyz", data["compass"]))) if use_mag else None
            return (dict(zip("xyz", data["accel"])), {"roll": roll, "pitch": pitch, "yaw": yaw},
                    dict(zip("xyz", data["gyro"])), mag, data["timestamp"] / 1e6)
        # Χωρίς πρόσβαση στο RTIMULib (π.χ. sense_emu): τρεις αναγνώσεις, χρόνος από το νήμα
        orientation = self.sense.get_orientation()
        accel = self.sense.get_accelerometer_raw()
        gyro = self.sense.get_gyroscope_raw()
        mag = self._read_magnet() if use_mag else None
        return accel, orientation, gyro, mag, None

    def toggle_track(self):
        # Start / Stop: πορτοκαλί όσο καταγράφει
        if self.track_sampler.running:
            self._stop_track()
        else:
            self.track_sampler.start()
            self.track_button.config(text="Stop", bg="orange", activebackground="orange")

    def _stop_track(self):
        self.track_sampler.stop()
        self.track_button.config(text="Start", **self.track_colors)

    def reset_track(self):
        self.tracker.reset()
        self.track_view.draw(self.tracker.snapshot())

    def _on_track_heading(self):
        # Αλλαγή Board/Gyro/Compass: η διαδρομή ξεκινάει από την αρχή στο νέο σύστημα αξόνων
        self.tracker.heading_mode = self.track_heading.get()
        self.reset_track()

    def track_loop(self):
        # Οθόνη του Track κάθε 50 ms (η μέτρηση γίνεται στο νήμα)
        if self._selected_tab() is self.track_tab and self.sense is not None:
            if self.track_sampler.error is not None:
                messagebox.showerror("Track", f"Sensor read failed: {self.track_sampler.error}")
                self.track_sampler.error = None
                self._stop_track()
            snapshot = self.tracker.snapshot()
            self._show_track_values(snapshot)
            self.track_view.draw(snapshot)
        self.root.after(50, self.track_loop)

    def _show_track_values(self, snap):
        up, right = snap["position"]
        names = ("N", "E") if snap["heading_mode"] in ("gyro", "compass") else ("F", "R")
        self.track_vars["speed"].set(f"Speed: {snap['speed'] * 100:.1f} cm/s")
        self.track_vars["distance"].set(f"Dist: {snap['distance'] * 100:.1f} cm")
        self.track_vars["position"].set(f"{names[0]}: {up * 100:.1f}  {names[1]}: {right * 100:.1f} cm")
        moving = self.track_sampler.running and not snap["still"]
        self.track_vars["state"].set("Moving" if moving else "Still")
        self.track_label_widgets["state"].config(fg="#d07000" if moving else "black",
                                                 font=self.bold_font if moving else "TkDefaultFont")

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
        # Επιταχυνσιόμετρο σε g (Sense HAT) ή οι sliders, κάθε 50 ms.
        # Linear: αφαίρεση της βαρύτητας με την κλίση από το get_orientation()
        if self._selected_tab() is self.accel_tab:
            if self.sense is not None:
                raw = self.sense.get_accelerometer_raw()
                if self.accel_mode.get() == "linear":
                    raw = acceleration.remove_gravity(raw, self.sense.get_orientation())
                    raw = self.accel_correction.apply(raw)
                    if not self.accel_correction.zeroing:
                        self.zero_button.config(**self.zero_colors)
            else:
                raw = {axis: var.get() for axis, var in self.accel["vars"].items()}
            self._show_accel_values(raw)
            self.accel["view"].draw(raw)
        self.root.after(50, self.accel_loop)

    @staticmethod
    def _show_axis_values(panel, raw):
        for axis in ("x", "y", "z"):
            value = "---" if raw is None else f"{round(raw[axis], panel['decimals']) + 0.0:.{panel['decimals']}f} {panel['unit']}"
            panel["labels"][axis].set(f"{axis.upper()}: {value}")

    def _show_magnet_values(self, raw):
        self._show_axis_values(self.magnet, raw)
        self._show_field(self.magnet["labels"]["total"], self.magnet["label_widgets"]["total"], "|B|", raw)

    def _show_accel_values(self, raw):
        # Raw: |a| ≈ 1 g σε ηρεμία (μόνο η βαρύτητα), σε όποια θέση κι αν είναι η πλακέτα.
        # Linear: |a| ≈ 0 σε ηρεμία
        self._show_axis_values(self.accel, raw)
        total = "---" if raw is None else f"{xyz_force.magnitude(raw):.2f} g"
        self.accel["labels"]["total"].set(f"|a|: {total}")

    def _show_field(self, var, label, title, raw):
        # Ένταση πεδίου |B| με προειδοποίηση όταν ένας μαγνήτης είναι πολύ κοντά:
        # πορτοκαλί πάνω από FIELD_WARN, κόκκινο με "too close!" πάνω από FIELD_DANGER,
        # και στις δύο περιπτώσεις με έντονη γραμματοσειρά
        # (εκεί κοντινά ατσάλινα μέρη μπορεί να μαγνητιστούν -> νέο hard-iron offset)
        field = None if raw is None else xyz_force.magnitude(raw)
        if field is None:
            var.set(f"{title}: ---")
        elif field > FIELD_DANGER:
            var.set(f"{title}: {field:.1f} µT  too close!")
        else:
            var.set(f"{title}: {field:.1f} µT")
        if field is not None and field > FIELD_DANGER:
            label.config(fg="red", font=self.bold_font)
        elif field is not None and field > FIELD_WARN:
            label.config(fg=FIELD_WARN_COLOR, font=self.bold_font)
        else:
            label.config(fg="black", font="TkDefaultFont")

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
