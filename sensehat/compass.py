"""Πυξίδα: υπολογισμός heading από το μαγνητόμετρο, hard-iron calibration,
και σχεδίαση σε Tk Canvas.

    view = CompassView(canvas)   # σχεδιάζει στον δοσμένο canvas (και σε κάθε resize)
    view.heading = 123.4         # μοίρες 0..360, ή None
    view.draw()

    cal = HardIronCalibration()  # φορτώνει τα αποθηκευμένα offsets
    raw = cal.correct(sense.get_compass_raw())
    cal.start() ... (περιστροφή της πλακέτας) ... updated = cal.stop()
"""
import json
import math
import os

BG_COLOR = "#1a1a1a"  # ίδιο με το φόντο της 3D σκηνής

# Hard-iron calibration: αρχείο με τα offsets (µT) δίπλα στο script, και ελάχιστο
# εύρος τιμών ανά άξονα στην καταγραφή για να θεωρηθεί ο άξονας βαθμονομημένος
HARD_IRON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pihat_gyro_hardiron.json")
HARD_IRON_MIN_SPAN = 20.0
AXES = ("x", "y", "z")

# Compass offset (μοίρες) ανά πηγή του North: "raw" (raw XY) και "fusion" (sense compass)
COMPASS_OFFSET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pihat_gyro_compass.json")
SOURCES = ("raw", "fusion")


class CompassOffsets:
    # Offsets που προστίθενται στο North ώστε να δείχνει τον πραγματικό βορρά, ένα για κάθε
    # πηγή (διαφέρουν, γιατί raw XY και RTIMULib μετράνε με διαφορετικό τρόπο).
    # Φορτώνονται από το αρχείο στη δημιουργία, αποθηκεύονται με save().
    def __init__(self, path=COMPASS_OFFSET_FILE):
        self.path = path
        self.values = self._load()

    def _load(self):
        try:
            with open(self.path) as f:
                data = json.load(f)
            return {source: float(data.get(source, 0.0)) for source in SOURCES}
        except (OSError, ValueError, TypeError, AttributeError):
            return {source: 0.0 for source in SOURCES}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.values, f, indent=2)


def raw_heading(raw):
    # Heading (0..360, αυξάνει δεξιόστροφα όπως η πυξίδα) από τα raw X/Y του
    # μαγνητόμετρου. Η γωνία atan2(y, x) μικραίνει όταν η πλακέτα στρίβει δεξιόστροφα,
    # γι' αυτό 360 - γωνία. Σωστό μόνο με την πλακέτα οριζόντια.
    return (360.0 - xy_angle(raw)) % 360.0


def xy_angle(raw):
    # Γωνία του διανύσματος X/Y του μαγνητόμετρου (0..360), για διάγνωση
    return math.degrees(math.atan2(raw["y"], raw["x"])) % 360.0


class HardIronCalibration:
    # Hard-iron offsets (µT) που αφαιρούνται από κάθε ανάγνωση του μαγνητόμετρου
    # (σταθερό πεδίο από μαγνητισμένα μέρη κοντά στον αισθητήρα).
    # start(): έναρξη καταγραφής -> περιστροφή της πλακέτας σε πλήρη κύκλο (ιδανικά
    # και με κλίσεις). stop(): offset = κέντρο (min+max)/2 ανά άξονα. Άξονες με μικρό
    # εύρος (π.χ. Z όταν η πλακέτα έμεινε οριζόντια) κρατούν το παλιό offset.
    def __init__(self, path=HARD_IRON_FILE, min_span=HARD_IRON_MIN_SPAN):
        self.path = path
        self.min_span = min_span
        self.offsets = self._load()
        self.record = None  # min/max ανά άξονα όσο γίνεται η καταγραφή

    @property
    def recording(self):
        return self.record is not None

    def correct(self, raw):
        # Διορθωμένη ανάγνωση. Όσο γίνεται καταγραφή, κρατάει min/max των αδιόρθωτων τιμών.
        if self.record is not None:
            for axis, (low, high) in self.record.items():
                self.record[axis] = (min(low, raw[axis]), max(high, raw[axis]))
        return {axis: raw[axis] - self.offsets[axis] for axis in AXES}

    def uncorrected(self, corrected):
        # Η αρχική ανάγνωση από μια διορθωμένη: το πεδίο που βλέπει πραγματικά ο αισθητήρας
        return {axis: corrected[axis] + self.offsets[axis] for axis in AXES}

    def start(self):
        self.record = {axis: (math.inf, -math.inf) for axis in AXES}

    def stop(self):
        # Τέλος καταγραφής: επιστρέφει τους άξονες που βαθμονομήθηκαν ([] = καμία αλλαγή).
        # Τα νέα offsets ισχύουν αμέσως· αν η αποθήκευση αποτύχει, πετάει OSError
        record, self.record = self.record, None
        if record is None:
            return []
        updated = [axis for axis, (low, high) in record.items() if high - low >= self.min_span]
        for axis in updated:
            low, high = record[axis]
            self.offsets[axis] = (low + high) / 2.0
        if updated:
            self._save()
        return updated

    def _load(self):
        try:
            with open(self.path) as f:
                data = json.load(f)
            return {axis: float(data[axis]) for axis in AXES}
        except (OSError, ValueError, KeyError, TypeError):
            return {axis: 0.0 for axis in AXES}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.offsets, f, indent=2)


class CompassView:
    def __init__(self, canvas, bg=BG_COLOR):
        self.canvas = canvas
        self.heading = None  # μοίρες, None = χωρίς τιμή (N στην κορυφή)
        canvas.config(bg=bg, highlightthickness=0)
        canvas.bind("<Configure>", lambda event: self.draw())

    def draw(self):
        # Πυξίδα: η ροδέλα στρέφεται ώστε το N να δείχνει τον πραγματικό βορρά,
        # το κίτρινο τρίγωνο πάνω είναι η κατεύθυνση της πλακέτας
        c = self.canvas
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
