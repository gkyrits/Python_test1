"""Γράφημα διανύσματος X/Y/Z (μαγνητόμετρο, επιταχυνσιόμετρο) σε Tk.

    view = XYZForceView(frame, value_range)   # φτιάχνει τους δύο canvas μέσα στο frame
    view.range_xy, view.range_z = 1.0, 2.0    # τιμή στο άκρο των αξόνων (προαιρετικά)
    view.draw({"x": ..., "y": ..., "z": ...})  # ή draw(None) μόνο για τους άξονες

Canvas 1: σταυρός με X οριζόντια (δεξιά +) και Y κάθετα (πάνω +).
Canvas 2 (στενότερος): Z κάθετα (πάνω +) πάνω σε οριζόντια γραμμή μηδέν.
"""
import math
import tkinter as tk

BG_COLOR = "#1a1a1a"  # ίδιο με το φόντο της 3D σκηνής
X_COLOR, Y_COLOR, Z_COLOR = "red", "#00c000", "#4080ff"  # όπως οι άξονες της 3D σκηνής


def magnitude(raw):
    # Μέτρο του διανύσματος |v| = sqrt(x² + y² + z²)
    return math.sqrt(raw["x"] ** 2 + raw["y"] ** 2 + raw["z"] ** 2)


class XYZForceView:
    def __init__(self, frame, value_range, size=250, z_width=80, bg=BG_COLOR):
        self.range_xy = value_range
        self.range_z = value_range
        self.raw = None  # τελευταία τιμή {x, y, z}
        self.xy = tk.Canvas(frame, width=size, height=size, bg=bg, highlightthickness=0)
        self.xy.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.z = tk.Canvas(frame, width=z_width, height=size, bg=bg, highlightthickness=0)
        self.z.pack(side=tk.LEFT, fill=tk.Y, padx=(2, 0))
        for canvas in (self.xy, self.z):
            canvas.bind("<Configure>", lambda event: self.draw())

    def draw(self, raw=None):
        # Βέλη με μήκος ανάλογο της τιμής. Οι άξονες έχουν ίδιο μήκος στην οθόνη, με τιμή
        # στο άκρο range_xy (X/Y) και range_z (Z). Γραμμές κλίμακας ανά range/4
        # (μεγαλύτερες ανά range/2), τιμές πέρα από το range σταματούν στο άκρο.
        # Χωρίς raw ξανασχεδιάζει την τελευταία τιμή (π.χ. σε resize ή αλλαγή κλίμακας).
        if raw is not None:
            self.raw = raw
        raw = self.raw
        xy, zc = self.xy, self.z
        w, h = xy.winfo_width(), xy.winfo_height()
        zw = zc.winfo_width()
        margin = 22
        reach = min(w, h) / 2.0 - margin  # μήκος μισού άξονα σε pixels
        if reach <= 0:
            return

        def axis_scale(value_range):
            step = value_range / 4.0
            ticks = [(i * step, 5 if i % 2 == 0 else 3) for i in range(-4, 5) if i]
            clamp = lambda v: max(-value_range, min(value_range, v))
            return reach / value_range, ticks, clamp

        # Canvas 1: σταυρός X/Y
        scale, ticks, clamp = axis_scale(self.range_xy)
        xy.delete("all")
        cx, cy = w / 2.0, h / 2.0
        xy.create_line(cx - reach, cy, cx + reach, cy, fill="gray50")
        xy.create_line(cx, cy - reach, cx, cy + reach, fill="gray50")
        for t, size in ticks:
            xy.create_line(cx + t * scale, cy - size, cx + t * scale, cy + size, fill="gray50")
            xy.create_line(cx - size, cy - t * scale, cx + size, cy - t * scale, fill="gray50")
        xy.create_text(cx + reach + 10, cy, text="X", fill=X_COLOR, font="TkDefaultFont 10 bold")
        xy.create_text(cx, cy - reach - 10, text="Y", fill=Y_COLOR, font="TkDefaultFont 10 bold")
        xy.create_text(cx + reach / 2.0, cy + 12, text=f"{self.range_xy / 2.0:g}",
                       fill="gray60", font="TkDefaultFont 7")
        if raw is not None:
            xy.create_line(cx, cy, cx + clamp(raw["x"]) * scale, cy, fill=X_COLOR, width=4,
                           arrow=tk.LAST, arrowshape=(10, 12, 5))
            xy.create_line(cx, cy, cx, cy - clamp(raw["y"]) * scale, fill=Y_COLOR, width=4,
                           arrow=tk.LAST, arrowshape=(10, 12, 5))

        # Canvas 2: οριζόντια γραμμή μηδέν του Z, βέλος πάνω (+) ή κάτω (-)
        scale, ticks, clamp = axis_scale(self.range_z)
        zc.delete("all")
        zx, zy = zw / 2.0, zc.winfo_height() / 2.0
        zc.create_line(4, zy, zw - 4, zy, fill="gray50")
        zc.create_line(zx, zy - reach, zx, zy + reach, fill="gray30", dash=(2, 3))
        for t, size in ticks:
            zc.create_line(zx - size, zy - t * scale, zx + size, zy - t * scale, fill="gray50")
        zc.create_text(zx, zy - reach - 10, text="Z", fill=Z_COLOR, font="TkDefaultFont 10 bold")
        zc.create_text(zx + 16, zy - reach / 2.0, text=f"{self.range_z / 2.0:g}",
                       fill="gray60", font="TkDefaultFont 7")
        if raw is not None:
            zc.create_line(zx, zy, zx, zy - clamp(raw["z"]) * scale, fill=Z_COLOR, width=4,
                           arrow=tk.LAST, arrowshape=(10, 12, 5))
