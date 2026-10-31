import math
import traceback
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


def tool_column(parent, commands):
    # Στήλη με τα μικρά κουμπιά (M/R/C, H/S) αριστερά από τον canvas. Επιστρέφει {κείμενο: κουμπί}.
    column = tk.Frame(parent)
    column.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
    buttons = {}
    for text, command in commands.items():
        button = tk.Button(column, text=text, width=2, height=2, padx=0, pady=0, command=command)
        button.pack(side=tk.TOP, pady=(10, 0))
        buttons[text] = button
    return buttons


def sunken_frame(parent):
    # Πλαίσιο με βυθισμένο περίγραμμα στο κάτω μέρος του tab (pack με side=BOTTOM: το πρώτο
    # που φτιάχνεται μπαίνει πιο κάτω)
    frame = tk.Frame(parent, relief=tk.SUNKEN, borderwidth=2)
    frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
    return frame


def button_colors(button):
    # Αρχικά χρώματα κουμπιού (bg, και activebackground που φαίνεται όσο το ποντίκι είναι πάνω του),
    # για επαναφορά μετά το πορτοκαλί "ενεργό"
    return {key: button.cget(key) for key in ("bg", "activebackground")}


class Tab:
    # Βάση για τα tabs του notebook. Κάθε tab:
    # - φτιάχνει το design του στο self.frame
    # - update(): καλείται κάθε period ms όσο το tab φαίνεται (False = η εφαρμογή έκλεισε)
    # - imu_config(): οι αισθητήρες του IMU (compass, gyroscope, accelerometer) που χρειάζεται
    # - hide(): όταν φεύγει κανείς από το tab, close(): στο κλείσιμο της εφαρμογής
    title = ""
    period = 50  # ms
    error = None  # το τελευταίο σφάλμα του update() (βλ. PiHatGyroApp._run)

    def __init__(self, app):
        self.app = app
        self.sense = app.sense
        self.frame = tk.Frame(app.notebook)
        app.notebook.add(self.frame, text=self.title)

    def update(self):
        return True

    def imu_config(self):
        return None

    def hide(self):
        pass

    def close(self):
        pass


class GyroscopeTab(Tab):
    # 3D σχήμα που ακολουθεί τον προσανατολισμό (Sense HAT) ή τους sliders
    title = "Gyroscope"
    period = 15

    def __init__(self, app):
        super().__init__(app)
        self.sensor = None  # τελευταία ανάγνωση του αισθητήρα (για το calibrate)

        # Η 3D σκηνή (σχήμα, άξονες, γράμματα) από το module gyro3d
        self.scene = gyro3d.GyroScene(CANVAS_WIDTH, CANVAS_HEIGHT, shape_size=SHAPE_SIZE, title=WINDOW_TITLE)

        # shape_frame: αριστερά τα κουμπιά, δεξιά ο canvas
        # (pack στο τέλος, μετά τα πλαίσια του κάτω μέρους, ώστε να παίρνει τον χώρο που μένει)
        shape_frame = tk.Frame(self.frame)
        # M = επόμενη προβολή του σχήματος, V = φόντο 360° on/off, R = reset offsets,
        # C = calibrate (το σχήμα γίνεται 0,0,0)
        self.buttons = tool_column(shape_frame, {"M": self.next_view, "V": self.toggle_scene,
                                                 "R": self.reset_offsets, "C": self.calibrate})
        self.scene_colors = button_colors(self.buttons["V"])
        self.canvas = tk.Canvas(shape_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=CANVAS_BG_COLOR,
                                highlightthickness=0)

        self.angle_titles = {"roll": "Roll (X)", "pitch": "Pitch (Y)", "yaw": "Yaw (Z)"}

        # Πλαίσιο με sliders: τιμές προσανατολισμού χωρίς Sense HAT, αλλιώς offsets
        control_frame = sunken_frame(self.frame)
        control_frame.columnconfigure(1, weight=1)
        title = "Orientation values" if self.sense is None else "Orientation offsets"
        tk.Label(control_frame, text=title, font=self.app.bold_font).grid(
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

        # Πλαίσιο με τις τρέχουσες τιμές Roll / Pitch / Yaw κάτω από τον canvas
        info_frame = sunken_frame(self.frame)
        self.angle_vars = {}
        for name, title in self.angle_titles.items():
            var = tk.StringVar(value=f"{title}: ---")
            # Πλάτος για το μεγαλύτερο κείμενο ("Pitch (Y): -180.0°"), ώστε να μην κόβεται ούτε να μετακινείται
            tk.Label(info_frame, textvariable=var, width=17, anchor=tk.W,
                     font="TkDefaultFont").pack(side=tk.LEFT, expand=True, padx=2, pady=1)
            self.angle_vars[name] = var

        shape_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.view_size = (CANVAS_WIDTH, CANVAS_HEIGHT)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas_image_id = self.canvas.create_image(0, 0, anchor=tk.NW)
        # Το όνομα της προβολής πάνω αριστερά στον canvas, με σκιά ώστε να διαβάζεται και πάνω στο φόντο 360°
        self.view_text_ids = [self.canvas.create_text(4 + d, 2 + d, anchor=tk.NW, text=self.scene.view.name,
                                                      fill=color, font="TkDefaultFont")
                              for d, color in ((1, "black"), (0, "gray80"))]
        self.tk_image = None

    def imu_config(self):
        return True, True, True

    def next_view(self):
        # M: η επόμενη προβολή του σχήματος (Axes, Solid, ...)
        name = self.scene.next_view()
        for text_id in self.view_text_ids:
            self.canvas.itemconfig(text_id, text=name)

    def toggle_scene(self):
        # V: φόντο με φωτογραφία 360° που γυρίζει με τον προσανατολισμό (πορτοκαλί όσο φαίνεται)
        visible = not self.scene.scene_visible
        try:
            self.scene.show_scene(visible)
        except Exception as e:  # π.χ. η φωτογραφία δεν φορτώνεται στη GPU
            traceback.print_exc()
            messagebox.showerror("Scene", f"Could not show the 360° scene:\n{type(e).__name__}: {e}")
            return
        if visible:
            self.buttons["V"].config(relief=tk.SUNKEN, bg="orange", activebackground="orange")
        else:
            self.buttons["V"].config(relief=tk.RAISED, **self.scene_colors)

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

    def update(self):
        # Χωρίς Sense HAT οι sliders δίνουν τις τιμές, αλλιώς είναι μια περιστροφή
        # offset που εφαρμόζεται πριν από αυτή του αισθητήρα: R = R_offset · R_sensor
        orientation = {name: var.get() for name, var in self.scale_vars.items()}
        scene_orientation = None
        if self.sense is not None:
            self.sensor = self.sense.get_orientation()
            orientation = matrix_to_euler(euler_to_matrix(orientation) @ euler_to_matrix(self.sensor))
            # Το φόντο 360° δείχνει τον πραγματικό κόσμο: η κλίση του αισθητήρα χωρίς τα offsets (C),
            # και yaw = heading της πλακέτας ως προς τον Βορρά (+ το Compass offset του "sense compass",
            # όπως στο Compass tab), ώστε το N της φωτογραφίας να είναι ο Βορράς
            scene_orientation = dict(self.sensor)
            scene_orientation["yaw"] += self.app.compass_offsets.values["fusion"]

        image = self.scene.render(orientation, self.view_size, scene_orientation)
        if image is None:  # η 3D σκηνή έκλεισε
            self.app.close()
            return False

        for name, var in self.angle_vars.items():
            var.set(f"{self.angle_titles[name]}: {round(orientation[name], 1) + 0.0:4.1f}°")
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(image))
        self.canvas.itemconfig(self.canvas_image_id, image=self.tk_image)
        return True

    def close(self):
        self.scene.close()


class CompassTab(Tab):
    # Πυξίδα: North από τα raw X/Y του μαγνητόμετρου ή το get_compass(), με Compass offset
    # ανά πηγή (S για αποθήκευση) και hard-iron calibration (H)
    title = "Compass"
    period = 20  # ανάγνωση κάθε 20 ms, οθόνη κάθε 2η φορά

    def __init__(self, app):
        super().__init__(app)
        offsets = app.compass_offsets

        # Από κάτω προς τα πάνω: το πλαίσιο με τον slider, το info_frame, και το compass_frame
        # Slider North: τιμή χωρίς Sense HAT, αλλιώς offset στο North της επιλεγμένης πηγής
        compass_control = sunken_frame(self.frame)
        compass_control.columnconfigure(1, weight=1)
        title = "Compass value" if self.sense is None else "Compass offset"
        tk.Label(compass_control, text=title, font=self.app.bold_font).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=2)
        # Πηγή του North: Raw = από τα raw X/Y του μαγνητόμετρου (πλακέτα οριζόντια),
        # sense compass = get_compass() από το fusion του RTIMULib (θέλει calibration με RTIMULibCal)
        self.source = tk.StringVar(value="raw")
        source_frame = tk.Frame(compass_control)
        source_frame.grid(row=0, column=1, columnspan=2, sticky=tk.E, padx=2)
        for text, value in (("Raw XY", "raw"), ("sense compass", "fusion")):
            tk.Radiobutton(source_frame, text=text, value=value, variable=self.source,
                           command=self._on_source,
                           padx=0, pady=0, borderwidth=0, highlightthickness=0,
                           state=tk.DISABLED if self.sense is None else tk.NORMAL
                           ).pack(side=tk.LEFT, padx=(6, 0))
        # Με Sense HAT ο slider είναι το offset της επιλεγμένης πηγής, χωρίς Sense HAT η τιμή North
        self.north_var = tk.DoubleVar(value=0.0 if self.sense is None else offsets.values["raw"])
        north_label = tk.Label(compass_control, text="0.0°", width=7, anchor=tk.E)
        tk.Label(compass_control, text="North", anchor=tk.W).grid(row=1, column=0, sticky=tk.W, padx=2)
        tk.Scale(compass_control, variable=self.north_var, from_=-180, to=180, resolution=0.1,
                 orient=tk.HORIZONTAL, showvalue=False, width=10, sliderlength=15, borderwidth=1
                 ).grid(row=1, column=1, sticky=tk.EW, padx=2)
        self.north_var.trace_add("write", lambda *_: north_label.config(
            text=f"{round(self.north_var.get(), 1) + 0.0:.1f}°"))
        self.north_var.trace_add("write", lambda *_: self._on_offset())
        north_label.config(text=f"{round(self.north_var.get(), 1) + 0.0:.1f}°")
        north_label.grid(row=1, column=2, padx=2)

        # Γραμμή 1: North + raw X/Y/Z. Γραμμή 2 (διάγνωση): ένταση πεδίου και
        # heading υπολογισμένο απευθείας από τα raw X/Y (χωρίς το fusion του RTIMULib)
        compass_info = sunken_frame(self.frame)
        self.vars = {}
        self.label_widgets = {}
        for names in (("north", "x", "y", "z"), ("field", "raw_heading")):
            row = tk.Frame(compass_info)
            row.pack(fill=tk.X)
            for name in names:
                var = tk.StringVar()
                label = tk.Label(row, textvariable=var, anchor=tk.W, font="TkDefaultFont")
                label.pack(side=tk.LEFT, padx=(4, 6), pady=0)
                self.vars[name] = var
                self.label_widgets[name] = label
        self._show_values(None, None)
        self.ticks = 0

        # compass_frame: αριστερά τα κουμπιά (όπως στο Gyroscope), δεξιά ο canvas
        compass_frame = tk.Frame(self.frame)
        compass_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        # H = hard-iron calibration του μαγνητόμετρου (πάτημα: έναρξη, περιστροφή, πάτημα: αποθήκευση)
        # S = αποθήκευση των Compass offsets (Raw XY και sense compass)
        self.buttons = tool_column(compass_frame, {"H": self.toggle_hard_iron, "S": self.save_offsets})
        self.hard_iron_colors = button_colors(self.buttons["H"])
        # Χωρίς Sense HAT δεν υπάρχει αισθητήρας για calibration ή offset
        if self.sense is None:
            self.buttons["H"].config(state=tk.DISABLED)
            self.buttons["S"].config(state=tk.DISABLED)
        # Σχεδίαση της πυξίδας από το module compass
        canvas = tk.Canvas(compass_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.view = compass.CompassView(canvas)

    def imu_config(self):
        return True, False, False  # μόνο μαγνητόμετρο (όπως το κάνει και το sense.get_compass())

    def update(self):
        # Χωρίς Sense HAT ο slider δίνει την τιμή North, αλλιώς προστίθεται ως offset.
        # Ανάγνωση κάθε 20 ms (το fusion του RTIMULib συγκλίνει με κάθε ανάγνωση),
        # αλλά ενημέρωση οθόνης κάθε 2η φορά (40 ms) για λιγότερη CPU
        north = self.north_var.get()
        raw = None
        if self.sense is not None:
            raw = self.app.read_magnet()
            if self.source.get() == "raw":
                north += compass.raw_heading(raw)
            else:
                north += self.sense.get_compass()
        self.view.heading = north % 360.0
        self.ticks += 1
        if self.ticks % 2 == 0:
            self._show_values(self.view.heading, raw)
            self.view.draw()
        return True

    def _show_values(self, heading, raw):
        self.vars["north"].set("North: ---" if heading is None else f"North: {round(heading, 1) % 360.0:.1f}°")
        for axis in ("x", "y", "z"):
            value = "---" if raw is None else f"{raw[axis]:.1f} µT"
            self.vars[axis].set(f"{axis.upper()}: {value}")
        # Διάγνωση: η ένταση του γήινου πεδίου είναι ~25-65 µT και μένει σταθερή όταν
        # η πλακέτα περιστρέφεται· το raw heading ισχύει μόνο με την πλακέτα οριζόντια
        xy_angle = "---" if raw is None else f"{compass.xy_angle(raw):.1f}°"
        self.app.show_field(self.vars["field"], self.label_widgets["field"], "Field |B|", raw)
        self.vars["raw_heading"].set(f"Raw XY heading: {xy_angle}")

    def _on_source(self):
        # Αλλαγή πηγής: ο slider δείχνει το offset της νέας πηγής
        self.north_var.set(self.app.compass_offsets.values[self.source.get()])

    def _on_offset(self):
        # Ο slider άλλαξε: κρατάει το offset της επιλεγμένης πηγής (το Raw XY πάει και στο Track)
        if self.sense is None:
            return
        self.app.compass_offsets.values[self.source.get()] = self.north_var.get()
        self.app.compass_offsets_changed()

    def save_offsets(self):
        # Κουμπί S: αποθήκευση και των δύο offsets, φορτώνονται ξανά στην επόμενη εκκίνηση
        offsets = self.app.compass_offsets
        try:
            offsets.save()
        except OSError as e:
            messagebox.showerror("Compass offset", f"Could not save: {e}")
            return
        messagebox.showinfo("Compass offset", f"Saved: Raw XY {offsets.values['raw']:.1f}°, "
                                              f"sense compass {offsets.values['fusion']:.1f}°")

    def toggle_hard_iron(self):
        # Κουμπί H: 1ο πάτημα έναρξη καταγραφής (περιστροφή της πλακέτας σε πλήρη κύκλο),
        # 2ο πάτημα υπολογισμός και αποθήκευση των offsets (βλ. compass.HardIronCalibration)
        hard_iron = self.app.hard_iron
        button = self.buttons["H"]
        if not hard_iron.recording:
            hard_iron.start()
            button.config(relief=tk.SUNKEN, bg="orange", activebackground="orange")
            return
        button.config(relief=tk.RAISED, **self.hard_iron_colors)
        try:
            updated = hard_iron.stop()
        except OSError as e:
            messagebox.showerror("Hard-iron calibration",
                                 f"The new offsets are used, but could not be saved:\n{e}")
            return
        if not updated:
            messagebox.showwarning("Hard-iron calibration",
                                   "Not enough rotation, the previous calibration is kept.\n"
                                   "Turn the board slowly through a full circle while recording.")
            return
        kept = [axis.upper() for axis in ("x", "y", "z") if axis not in updated]
        offsets = ", ".join(f"{axis.upper()}: {hard_iron.offsets[axis]:.1f} µT" for axis in ("x", "y", "z"))
        messagebox.showinfo("Hard-iron calibration",
                            f"Offsets: {offsets}" + (f"\nKept previous: {', '.join(kept)} (small range)" if kept else ""))


class VectorTab(Tab):
    # Κοινό design για Magnetometer και Accelerometer: από κάτω προς τα πάνω (pack με
    # side=BOTTOM) οι sliders προσομοίωσης (μόνο χωρίς Sense HAT), το πλαίσιο επιλογών
    # (αν δοθεί range_choices), το info_frame, και το frame με τους δύο canvas:
    # X/Y σε σταυρό και Z σε στενότερο canvas (module xyz_force)
    unit = ""
    value_range = 1.0
    resolution = 0.1
    decimals = 1
    range_choices = None

    def __init__(self, app):
        super().__init__(app)
        unit, decimals, value_range = self.unit, self.decimals, self.value_range
        self.vars = {}           # sliders προσομοίωσης (χωρίς Sense HAT)
        self.labels = {}         # x, y, z, total
        self.label_widgets = {}
        self.options = None      # πλαίσιο επιλογών (αν υπάρχει range_choices)

        if self.sense is None:
            control = sunken_frame(self.frame)
            control.columnconfigure(1, weight=1)
            tk.Label(control, text=f"{self.title} values", font=self.app.bold_font).grid(
                row=0, column=0, columnspan=3, sticky=tk.W, padx=2)
            for row, axis in enumerate(("x", "y", "z"), start=1):
                var = tk.DoubleVar(value=0.0)
                value_label = tk.Label(control, text=f"{0:.{decimals}f} {unit}", width=9, anchor=tk.E)
                tk.Label(control, text=axis.upper(), anchor=tk.W).grid(row=row, column=0, sticky=tk.W, padx=2)
                tk.Scale(control, variable=var, from_=-value_range, to=value_range, resolution=self.resolution,
                         orient=tk.HORIZONTAL, showvalue=False, width=10, sliderlength=15, borderwidth=1
                         ).grid(row=row, column=1, sticky=tk.EW, padx=2)
                var.trace_add("write", lambda *_, v=var, lbl=value_label: lbl.config(
                    text=f"{round(v.get(), decimals) + 0.0:.{decimals}f} {unit}"))
                value_label.grid(row=row, column=2, padx=2)
                self.vars[axis] = var

        if self.range_choices:
            # Πλαίσιο επιλογών: γραμμή με τη μέγιστη τιμή στο άκρο των αξόνων, ξεχωριστά
            # για τον σταυρό X/Y και τον Z (επιπλέον γραμμές μπαίνουν στο self.options)
            self.options = sunken_frame(self.frame)
            range_frame = tk.Frame(self.options)
            range_frame.pack(side=tk.BOTTOM, fill=tk.X)
            tk.Label(range_frame, text="Axes range", font=self.app.bold_font).pack(side=tk.LEFT, padx=(4, 8))
            for key, text in (("range_xy", "X/Y:"), ("range_z", "Z:")):
                values, default = self.range_choices[key]
                tk.Label(range_frame, text=text).pack(side=tk.LEFT, padx=(4, 2))
                choice = ttk.Combobox(range_frame, values=[f"{v:g}" for v in values], width=4, state="readonly")
                choice.set(f"{default:g}")
                choice.pack(side=tk.LEFT, pady=1)
                tk.Label(range_frame, text=unit).pack(side=tk.LEFT, padx=(2, 6))

                def on_select(event, key=key, choice=choice):
                    setattr(self.view, key, float(choice.get()))
                    self.view.draw()
                choice.bind("<<ComboboxSelected>>", on_select)

        info = sunken_frame(self.frame)
        for name in ("x", "y", "z", "total"):
            var = tk.StringVar()
            label = tk.Label(info, textvariable=var, anchor=tk.W, font="TkDefaultFont")
            label.pack(side=tk.LEFT, padx=(4, 6), pady=0)
            self.labels[name] = var
            self.label_widgets[name] = label

        canvas_frame = tk.Frame(self.frame)
        canvas_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        self.view = xyz_force.XYZForceView(canvas_frame, value_range, size=CANVAS_HEIGHT)
        if self.range_choices:
            for key, (values, default) in self.range_choices.items():
                setattr(self.view, key, default)

    def slider_values(self):
        return {axis: var.get() for axis, var in self.vars.items()}

    def show_axis_values(self, raw):
        for axis in ("x", "y", "z"):
            value = "---" if raw is None else f"{round(raw[axis], self.decimals) + 0.0:.{self.decimals}f} {self.unit}"
            self.labels[axis].set(f"{axis.upper()}: {value}")


class MagnetometerTab(VectorTab):
    # Raw μαγνητόμετρο (με hard-iron διόρθωση) σε µT, με προειδοποίηση |B| κοντά σε μαγνήτη
    title = "Magnetometer"
    unit = "µT"
    value_range = MAGNET_RANGE
    resolution = 0.1
    decimals = 1

    def __init__(self, app):
        super().__init__(app)
        self.show_values(None)

    def imu_config(self):
        return True, False, False  # μόνο μαγνητόμετρο

    def update(self):
        # Raw μαγνητόμετρο (Sense HAT, με hard-iron διόρθωση) ή οι sliders, κάθε 50 ms
        raw = self.app.read_magnet() if self.sense is not None else self.slider_values()
        self.show_values(raw)
        self.view.draw(raw)
        return True

    def show_values(self, raw):
        self.show_axis_values(raw)
        self.app.show_field(self.labels["total"], self.label_widgets["total"], "|B|", raw)


class AccelerometerTab(VectorTab):
    # Επιταχυνσιόμετρο σε g: Raw (με τη βαρύτητα, και έλεγχο βαθμονόμησης) ή Linear
    # (χωρίς βαρύτητα, με Zero / Auto-zero), και επιλογή κλίμακας αξόνων
    title = "Accelerometer"
    unit = "g"
    value_range = ACCEL_RANGE
    resolution = 0.01
    decimals = 2
    range_choices = ACCEL_RANGE_CHOICES

    def __init__(self, app):
        # Raw = μέτρηση όπως είναι (με τη βαρύτητα), Linear = χωρίς βαρύτητα σε X, Y, Z
        # (acceleration.GravityTracker: βαρύτητα μετρημένη στις στάσεις, gyroscope στην κίνηση).
        # Χωρίς Sense HAT δεν υπάρχει gyroscope για την αφαίρεση, οπότε μόνο Raw.
        self.mode = None
        super().__init__(app)
        self.mode = tk.StringVar(value="raw")
        self.gravity_tracker = acceleration.GravityTracker()
        # Διόρθωση υπολοίπου στο Linear: Zero = μέσος όρος ~1 s με την πλακέτα ακίνητη,
        # Auto-zero = αργό φίλτρο που αφαιρεί συνεχώς ό,τι μένει σταθερό
        self.correction = acceleration.ResidualCorrection()
        # Έλεγχος βαθμονόμησης στο Raw: |a| ≈ 1 g με την πλακέτα ακίνητη
        self.gravity_check = acceleration.GravityCheck()

        mode_frame = tk.Frame(self.options)
        mode_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(mode_frame, text="Mode", font=self.app.bold_font).pack(side=tk.LEFT, padx=(4, 8))
        for text, value in (("Raw", "raw"), ("Linear (gravity removed)", "linear")):
            tk.Radiobutton(mode_frame, text=text, value=value, variable=self.mode, command=self._on_mode,
                           padx=0, pady=0, borderwidth=0, highlightthickness=0,
                           state=tk.DISABLED if self.sense is None else tk.NORMAL
                           ).pack(side=tk.LEFT, padx=(4, 8), pady=1)
        correction_frame = tk.Frame(self.options)
        correction_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(correction_frame, text="Residual", font=self.app.bold_font).pack(side=tk.LEFT, padx=(4, 8))
        self.zero_button = tk.Button(correction_frame, text="Zero", padx=6, pady=0, command=self.zero)
        self.zero_button.pack(side=tk.LEFT, padx=(4, 8), pady=1)
        self.zero_colors = button_colors(self.zero_button)
        self.auto_zero_var = tk.BooleanVar(value=False)
        self.auto_zero_check = tk.Checkbutton(correction_frame, text="Auto-zero", variable=self.auto_zero_var,
                                              command=self._on_auto_zero, padx=0, pady=0,
                                              borderwidth=0, highlightthickness=0)
        self.auto_zero_check.pack(side=tk.LEFT, padx=(4, 8))
        self._update_correction_controls()
        self.show_values(None)

    def linear(self):
        return self.mode is not None and self.mode.get() == "linear"

    def imu_config(self):
        # Raw: μόνο επιταχυνσιόμετρο. Linear: + gyroscope, για την κλίση στην κίνηση
        return False, self.linear(), True

    def update(self):
        # Επιταχυνσιόμετρο σε g (Sense HAT) ή οι sliders, κάθε 50 ms.
        # Linear: αφαίρεση της βαρύτητας με δική του κλίση (όχι το get_orientation(), που μετά
        # από αλλαγή tab χρειάζεται χρόνο να ηρεμήσει και αφήνει 0.1-0.2 g βαρύτητας)
        if self.sense is not None:
            raw = self.sense.get_accelerometer_raw()
            if self.linear():
                raw = self.gravity_tracker.update(raw, self.sense.get_gyroscope_raw())
                raw = self.correction.apply(raw)
                if not self.correction.zeroing:
                    self.zero_button.config(**self.zero_colors)
            else:
                self.gravity_check.update(raw)
        else:
            raw = self.slider_values()
        self.show_values(raw)
        self.view.draw(raw)
        return True

    def show_values(self, raw):
        # Raw: |a| ≈ 1 g σε ηρεμία (μόνο η βαρύτητα), σε όποια θέση κι αν είναι η πλακέτα.
        # Linear: |a| ≈ 0 σε ηρεμία
        self.show_axis_values(raw)
        total = "---" if raw is None else f"{xyz_force.magnitude(raw):.2f} g"
        # Raw με Sense HAT: προειδοποίηση αν με την πλακέτα ακίνητη το |a| δεν είναι ≈ 1 g
        warn = (raw is not None and self.sense is not None and not self.linear()
                and not self.gravity_check.ok)
        self.labels["total"].set(f"|a|: {total}" + ("  check calibration!" if warn else ""))
        self.label_widgets["total"].config(fg=FIELD_WARN_COLOR if warn else "black",
                                           font=self.app.bold_font if warn else "TkDefaultFont")

    def _on_mode(self):
        # Αλλαγή Raw/Linear: νέες ρυθμίσεις IMU, και κλίση/υπόλοιπο μετριούνται από την αρχή
        self.gravity_tracker.reset()
        self.correction.reset()
        self.gravity_check.reset()
        self.zero_button.config(**self.zero_colors)
        self._update_correction_controls()
        self.app.apply_imu_config()

    def _update_correction_controls(self):
        # Zero / Auto-zero έχουν νόημα μόνο στο Linear (και μόνο με Sense HAT)
        state = tk.NORMAL if self.linear() else tk.DISABLED
        self.zero_button.config(state=state)
        self.auto_zero_check.config(state=state)

    def zero(self):
        # Κουμπί Zero: μέσος όρος ~1 s (πορτοκαλί όσο μετράει), η πλακέτα πρέπει να μένει ακίνητη
        self.correction.start_zero()
        self.zero_button.config(bg="orange", activebackground="orange")

    def _on_auto_zero(self):
        self.correction.auto = self.auto_zero_var.get()


class TrackTab(Tab):
    # Ταχύτητα και διαδρομή από τη γραμμική επιτάχυνση (module track: ZUPT, διόρθωση drift
    # σε κάθε στάση, δική του κλίση), με τη μέτρηση σε νήμα και την οθόνη κάθε 50 ms
    title = "Track"
    period = 50

    def __init__(self, app):
        super().__init__(app)
        self.tracker = track.Tracker()
        # Το Track διαβάζει το μαγνητόμετρο απευθείας (όπως η πηγή Raw XY), οπότε παίρνει εκείνο το offset
        self.set_heading_offset()
        self.sampler = track.TrackSampler(self._read_sample, self.tracker)

        # Από κάτω προς τα πάνω: οι επιλογές, το info_frame, και το frame με τον canvas
        options = sunken_frame(self.frame)
        state = tk.DISABLED if self.sense is None else tk.NORMAL
        buttons_row = tk.Frame(options)
        buttons_row.pack(fill=tk.X)
        self.start_button = tk.Button(buttons_row, text="Start", width=6, padx=2, pady=0,
                                      command=self.toggle, state=state)
        self.start_button.pack(side=tk.LEFT, padx=(4, 4), pady=1)
        self.start_colors = button_colors(self.start_button)
        tk.Button(buttons_row, text="Reset", width=6, padx=2, pady=0, command=self.reset,
                  state=state).pack(side=tk.LEFT, padx=(0, 8), pady=1)
        # Board: άξονες της πλακέτας (πάνω = μπροστά, χωρίς στροφές), Gyro: Βορράς πάνω, αρχή από την
        # πυξίδα και στροφές από το gyroscope, Compass: Βορράς πάνω (μαγνητόμετρο με διόρθωση κλίσης)
        heading_row = tk.Frame(options)
        heading_row.pack(fill=tk.X)
        tk.Label(heading_row, text="Heading", font=self.app.bold_font).pack(side=tk.LEFT, padx=(4, 4))
        self.heading = tk.StringVar(value="board")
        for text, value in (("Board", "board"), ("Gyro", "gyro"), ("Compass", "compass")):
            tk.Radiobutton(heading_row, text=text, value=value, variable=self.heading,
                           command=self._on_heading, padx=0, pady=0, borderwidth=0,
                           highlightthickness=0, state=state).pack(side=tk.LEFT, padx=(4, 4), pady=1)

        info = sunken_frame(self.frame)
        self.vars = {}
        self.label_widgets = {}
        for name in ("speed", "distance", "position", "state"):
            var = tk.StringVar()
            label = tk.Label(info, textvariable=var, anchor=tk.W, font="TkDefaultFont")
            label.pack(side=tk.LEFT, padx=(4, 6), pady=0)
            self.vars[name] = var
            self.label_widgets[name] = label
        self._show_values(self.tracker.snapshot())

        track_frame = tk.Frame(self.frame)
        track_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(track_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        canvas.pack(fill=tk.BOTH, expand=True)
        self.view = track.TrackView(canvas)
        if self.sense is None:
            self.view.message = "Track needs a Sense HAT"

    def imu_config(self):
        return True, True, True

    def set_heading_offset(self):
        self.tracker.heading_offset = self.app.compass_offsets.values["raw"] if self.sense is not None else 0.0

    def _read_sample(self):
        # Καλείται από το νήμα του Track: (επιτάχυνση g, gyroscope rad/s, μαγνητόμετρο µT με
        # hard-iron διόρθωση ή None, χρόνος s ή None), ή None χωρίς νέο δείγμα.
        # Αν γίνεται, ΜΙΑ ανάγνωση του RTIMULib για όλα (ίδια στιγμή, χρόνος του IMU, πιο
        # γρήγορα), αντί για τρεις ξεχωριστές αναγνώσεις μέσω του sense_hat.
        use_mag = self.tracker.heading_mode in ("gyro", "compass")  # Gyro: αρχική κατεύθυνση από την πυξίδα
        imu = getattr(self.sense, "_imu", None)
        if imu is not None and hasattr(imu, "getIMUData"):
            if not imu.IMURead():
                return None
            data = imu.getIMUData()
            mag = self.app.hard_iron.correct(dict(zip("xyz", data["compass"]))) if use_mag else None
            return (dict(zip("xyz", data["accel"])), dict(zip("xyz", data["gyro"])), mag,
                    data["timestamp"] / 1e6)
        # Χωρίς πρόσβαση στο RTIMULib (π.χ. sense_emu): δύο ή τρεις αναγνώσεις, χρόνος από το νήμα
        accel = self.sense.get_accelerometer_raw()
        gyro = self.sense.get_gyroscope_raw()
        mag = self.app.read_magnet() if use_mag else None
        return accel, gyro, mag, None

    def toggle(self):
        # Start / Stop: πορτοκαλί όσο καταγράφει
        if self.sampler.running:
            self.stop()
        else:
            self.sampler.start()
            self.start_button.config(text="Stop", bg="orange", activebackground="orange")

    def stop(self):
        self.sampler.stop()
        self.start_button.config(text="Start", **self.start_colors)

    def reset(self):
        self.tracker.reset()
        self.view.draw(self.tracker.snapshot())

    def _on_heading(self):
        # Αλλαγή Board/Gyro/Compass: η διαδρομή ξεκινάει από την αρχή στο νέο σύστημα αξόνων
        self.tracker.heading_mode = self.heading.get()
        self.reset()

    def update(self):
        # Οθόνη του Track κάθε 50 ms (η μέτρηση γίνεται στο νήμα)
        if self.sense is None:
            return True
        if self.sampler.error is not None:
            messagebox.showerror("Track", f"Sensor read failed: {self.sampler.error}")
            self.sampler.error = None
            self.stop()
        snapshot = self.tracker.snapshot()
        self._show_values(snapshot)
        self.view.draw(snapshot)
        return True

    def _show_values(self, snap):
        up, right = snap["position"]
        names = ("N", "E") if snap["heading_mode"] in ("gyro", "compass") else ("F", "R")
        self.vars["speed"].set(f"Speed: {snap['speed'] * 100:.1f} cm/s")
        self.vars["distance"].set(f"Dist: {snap['distance'] * 100:.1f} cm")
        self.vars["position"].set(f"{names[0]}: {up * 100:.1f}  {names[1]}: {right * 100:.1f} cm")
        moving = self.sampler.running and not snap["still"]
        self.vars["state"].set("Moving" if moving else "Still")
        self.label_widgets["state"].config(fg="#d07000" if moving else "black",
                                           font=self.app.bold_font if moving else "TkDefaultFont")

    def hide(self):
        # Το νήμα διαβάζει τον αισθητήρα και δεν πρέπει να τρέχει μαζί με τα άλλα tabs
        self.stop()

    def close(self):
        self.sampler.stop()


class PiHatGyroApp:
    # Το παράθυρο: Sense HAT, notebook με τα tabs, κοινά calibrations (hard-iron, Compass
    # offsets), αισθητήρες του IMU ανά tab και το loop κάθε tab
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)

        if SenseHat is not None:
            self.sense = SenseHat()
            self.sense.clear()
        else:
            self.sense = None

        # Έντονη εκδοχή της γραμματοσειράς του GUI (για τις προειδοποιήσεις)
        self.bold_font = tkfont.nametofont("TkDefaultFont").copy()
        self.bold_font.configure(weight="bold")

        # Κοινά για Compass, Magnetometer και Track (module compass, από τα αρχεία τους):
        # hard-iron calibration του μαγνητόμετρου (H) και Compass offset ανά πηγή (S)
        self.hard_iron = compass.HardIronCalibration()
        self.compass_offsets = compass.CompassOffsets()

        # Notebook με μικρά tabs (ίδια γραμματοσειρά με το υπόλοιπο GUI, μικρό ύψος tab)
        style = ttk.Style(root)
        style.configure("Small.TNotebook", tabmargins=(2, 2, 2, 0))
        style.configure("Small.TNotebook.Tab", font="TkDefaultFont", padding=(6, 0))
        self.notebook = ttk.Notebook(root, style="Small.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.gyro_tab = GyroscopeTab(self)
        self.compass_tab = CompassTab(self)
        self.magnet_tab = MagnetometerTab(self)
        self.accel_tab = AccelerometerTab(self)
        self.track_tab = TrackTab(self)
        self.tabs = (self.gyro_tab, self.compass_tab, self.magnet_tab, self.accel_tab, self.track_tab)

        self.notebook.bind("<<NotebookTabChanged>>", lambda event: self._on_tab_changed())
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        for tab in self.tabs:
            self._run(tab)

    def _run(self, tab):
        # Loop του tab: update() κάθε tab.period ms, μόνο όσο το tab φαίνεται
        # (λιγότερη CPU, και κάθε tab διαβάζει μόνο με τους δικούς του αισθητήρες ενεργούς)
        if self.selected_tab() is tab:
            try:
                if tab.update() is False:
                    return  # η εφαρμογή έκλεισε
                if tab.error is not None:  # δουλεύει ξανά
                    tab.error = None
                    self.root.title(WINDOW_TITLE)
            except Exception as e:
                # Π.χ. σφάλμα I2C: το loop συνεχίζει. Το σφάλμα φαίνεται στον τίτλο του παραθύρου,
                # και γράφεται στην κονσόλα μία φορά (μέχρι να αλλάξει ή να ξαναδουλέψει το tab)
                error = f"{type(e).__name__}: {e}"
                if error != tab.error:
                    traceback.print_exc()
                    tab.error = error
                    self.root.title(f"{WINDOW_TITLE} - {tab.title} error: {error}")
        self.root.after(tab.period, lambda: self._run(tab))

    def _on_tab_changed(self):
        # Το σφάλμα στον τίτλο αφορά το tab που έφυγε (δεν τρέχει πια): καθαρίζει,
        # και ξαναγράφεται αν το νέο tab έχει κι αυτό σφάλμα
        for tab in self.tabs:
            tab.error = None
        self.root.title(WINDOW_TITLE)
        self.apply_imu_config()

    def selected_tab(self):
        widget = self.notebook.nametowidget(self.notebook.select())
        return next((tab for tab in self.tabs if tab.frame is widget), None)

    def apply_imu_config(self):
        # Αισθητήρες του IMU για το tab που φαίνεται: set_imu_config(compass, gyroscope, accelerometer).
        # Τα υπόλοιπα tabs παίρνουν hide() (π.χ. το Track σταματάει το νήμα του).
        if self.sense is None:
            return
        current = self.selected_tab()
        for tab in self.tabs:
            if tab is not current:
                tab.hide()
        config = current.imu_config() if current is not None else None
        if config is not None:
            self.sense.set_imu_config(*config)

    def read_magnet(self):
        # Ανάγνωση του μαγνητόμετρου (µT) διορθωμένη με τα hard-iron offsets (module compass)
        return self.hard_iron.correct(self.sense.get_compass_raw())

    def compass_offsets_changed(self):
        # Το Compass offset της πηγής Raw XY ισχύει και για το heading του Track
        if hasattr(self, "track_tab"):
            self.track_tab.set_heading_offset()

    def show_field(self, var, label, title, raw):
        # Ένταση πεδίου |B| με προειδοποίηση όταν ένας μαγνήτης είναι πολύ κοντά:
        # πορτοκαλί πάνω από FIELD_WARN, κόκκινο με "too close!" πάνω από FIELD_DANGER,
        # και στις δύο περιπτώσεις με έντονη γραμματοσειρά
        # (εκεί κοντινά ατσάλινα μέρη μπορεί να μαγνητιστούν -> νέο hard-iron offset).
        # Το raw είναι διορθωμένο με το hard-iron (το γήινο πεδίο, ~25-65 µT), αλλά η προειδοποίηση
        # κρίνεται από το πεδίο που βλέπει ο αισθητήρας, χωρίς τη διόρθωση (sensor), που
        # φαίνεται σε παρένθεση όταν υπάρχει προειδοποίηση, π.χ. "|B|: 47.2 µT (159)"
        field = None if raw is None else xyz_force.magnitude(raw)
        sensor = field
        if raw is not None and self.sense is not None:
            sensor = xyz_force.magnitude(self.hard_iron.uncorrected(raw))
        if field is None:
            var.set(f"{title}: ---")
        else:
            text = f"{title}: {field:.1f} µT"
            if sensor > FIELD_WARN and abs(sensor - field) >= 0.05:
                text += f" ({sensor:.0f})"
            var.set(text + (" too close!" if sensor > FIELD_DANGER else ""))
        if field is not None and sensor > FIELD_DANGER:
            label.config(fg="red", font=self.bold_font)
        elif field is not None and sensor > FIELD_WARN:
            label.config(fg=FIELD_WARN_COLOR, font=self.bold_font)
        else:
            label.config(fg="black", font="TkDefaultFont")

    def close(self):
        for tab in self.tabs:
            tab.close()
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    app = PiHatGyroApp(window)
    window.mainloop()
