import math
import tkinter as tk
from tkinter import ttk
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


WINDOW_TITLE = "Sense Gyroscope"

CANVAS_BG_COLOR = "light gray"
CANVAS_WIDTH = 350
CANVAS_HEIGHT = 250
COMPASS_BG_COLOR = "#1a1a1a"  # ίδιο με το φόντο της 3D σκηνής

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
        # Κενά (προς το παρόν) tabs
        for text in ("Accelerometer", "Magnetometer"):
            notebook.add(tk.Frame(notebook), text=text)
        notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.notebook, self.gyro_tab, self.compass_tab = notebook, gyro_tab, compass_tab

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
            row=0, column=0, columnspan=3, sticky=tk.W, padx=2)
        self.north_var = tk.DoubleVar(value=0.0)
        north_label = tk.Label(compass_control, text="0.0°", width=7, anchor=tk.E)
        tk.Label(compass_control, text="North", anchor=tk.W).grid(row=1, column=0, sticky=tk.W, padx=2)
        tk.Scale(compass_control, variable=self.north_var, from_=0, to=360, resolution=0.1,
                 orient=tk.HORIZONTAL, showvalue=False, width=10, sliderlength=15, borderwidth=1
                 ).grid(row=1, column=1, sticky=tk.EW, padx=2)
        self.north_var.trace_add("write", lambda *_: north_label.config(
            text=f"{round(self.north_var.get(), 1) + 0.0:.1f}°"))
        north_label.grid(row=1, column=2, padx=2)

        compass_info = tk.Frame(compass_tab, relief=tk.SUNKEN, borderwidth=2)
        compass_info.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        self.compass_vars = {}
        for name in ("north", "x", "y", "z"):
            var = tk.StringVar()
            tk.Label(compass_info, textvariable=var, anchor=tk.W,
                     font="TkDefaultFont").pack(side=tk.LEFT, padx=(4, 6), pady=0)
            self.compass_vars[name] = var
        self._show_compass_values(None, None)
        compass_frame = tk.Frame(compass_tab)
        compass_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        self.compass_canvas = tk.Canvas(compass_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                                        bg=COMPASS_BG_COLOR, highlightthickness=0)
        self.compass_canvas.pack(fill=tk.BOTH, expand=True)
        self.compass_canvas.bind("<Configure>", lambda event: self._draw_compass())

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.render_loop()
        self.compass_loop()

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
        # Compass:   μόνο μαγνητόμετρο (όπως το κάνει και το sense.get_compass())
        # Gyroscope: gyroscope + accelerometer, χωρίς μαγνητόμετρο
        if self.sense is None:
            return
        tab = self._selected_tab()
        if tab is self.compass_tab:
            self.sense.set_imu_config(True, False, False)
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
        # Χωρίς Sense HAT ο slider δίνει την τιμή North, αλλιώς προστίθεται ως offset
        if self._selected_tab() is self.compass_tab:
            north = self.north_var.get()
            raw = None
            if self.sense is not None:
                north += self.sense.get_compass()
                raw = self.sense.get_compass_raw()
            self.heading = north % 360.0
            self._show_compass_values(self.heading, raw)
            self._draw_compass()
        self.root.after(100, self.compass_loop)

    def _show_compass_values(self, heading, raw):
        self.compass_vars["north"].set("North: ---" if heading is None else f"North: {round(heading, 1) % 360.0:.1f}°")
        for axis in ("x", "y", "z"):
            value = "---" if raw is None else f"{raw[axis]:.1f} µT"
            self.compass_vars[axis].set(f"{axis.upper()}: {value}")

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
