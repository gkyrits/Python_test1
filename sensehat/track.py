"""Εκτίμηση ταχύτητας και διαδρομής από το επιταχυνσιόμετρο (dead reckoning με ZUPT).

Η γραμμική επιτάχυνση ολοκληρώνεται μία φορά για ταχύτητα και δεύτερη για θέση. Κάθε
μικρό υπόλοιπο σφάλμα μεγαλώνει γρήγορα (0.01 g -> ~5 cm σε 1 s, ~1.2 m σε 5 s), γι' αυτό:
- ZUPT (zero velocity update): όταν η πλακέτα είναι ακίνητη η ταχύτητα γίνεται 0, οπότε
  το σφάλμα μαζεύεται μόνο για τη διάρκεια κάθε κίνησης
- όσο είναι ακίνητη, μετριέται το υπόλοιπο (bias) και αφαιρείται στην κίνηση
Καλά αποτελέσματα: σπρωξίματα σε τραπέζι με στάσεις ανάμεσα. Όχι: συνεχής κίνηση.

    tracker = Tracker()
    sampler = TrackSampler(read_sample, tracker)   # νήμα ~100 Hz
    sampler.start() ... sampler.stop()
    view = TrackView(canvas)
    view.draw(tracker.snapshot())

read_sample() επιστρέφει (accel σε g, orientation σε μοίρες, gyro σε rad/s, heading ή None),
όλα με τη σύμβαση της Sense HAT. heading = μοίρες δεξιόστροφα από τον Βορρά της
κατεύθυνσης της πλακέτας (άξονας X), ή None για διαδρομή στους άξονες της πλακέτας.
"""
import math
import threading
import time

G = 9.80665  # m/s² ανά g

# Ανίχνευση ακινησίας (ZUPT): |γραμμική επιτάχυνση| και |περιστροφή| κάτω από τα όρια
# για STILL_TIME δευτερόλεπτα
STILL_ACCEL = 0.03  # g
STILL_GYRO = 0.15   # rad/s (~9°/s)
STILL_TIME = 0.15   # s
BIAS_TAU = 0.5      # s, σταθερά χρόνου για τη μέτρηση του υπολοίπου όσο είναι ακίνητη
PATH_STEP = 0.002   # m, ελάχιστη απόσταση για νέο σημείο στη διαδρομή

# Αν στην πράξη η διαδρομή βγαίνει καθρεφτισμένη αριστερά/δεξιά, αλλάζει σε -1.0
LEFT_SIGN = 1.0


def level_acceleration(accel, orientation):
    # Επιτάχυνση (m/s²) σε οριζόντιο σύστημα: x = μπροστά (άξονας X της πλακέτας στο
    # οριζόντιο επίπεδο), y = αριστερά, z = πάνω, χωρίς τη βαρύτητα. Αναιρεί roll και pitch
    # (σύμβαση RTIMULib, Z-Y-X) ώστε να μη μετράει η κλίση της πλακέτας.
    r = math.radians(orientation["roll"])
    p = math.radians(orientation["pitch"])
    ax, ay, az = accel["x"], accel["y"], accel["z"]
    y1 = ay * math.cos(r) - az * math.sin(r)
    z1 = ay * math.sin(r) + az * math.cos(r)
    x2 = ax * math.cos(p) + z1 * math.sin(p)
    z2 = -ax * math.sin(p) + z1 * math.cos(p)
    return x2 * G, LEFT_SIGN * y1 * G, (z2 - 1.0) * G


def to_output_frame(forward, left, heading):
    # (μπροστά, αριστερά) -> (πάνω, δεξιά) στο γράφημα: χωρίς heading οι άξονες της
    # πλακέτας (πάνω = μπροστά), με heading (Βορράς, Ανατολή)
    if heading is None:
        return forward, -left
    h = math.radians(heading)
    north = forward * math.cos(h) + left * math.sin(h)
    east = forward * math.sin(h) - left * math.cos(h)
    return north, east


class Tracker:
    # Ταχύτητα και θέση στο οριζόντιο επίπεδο (m/s, m): "up" = μπροστά ή Βορράς,
    # "right" = δεξιά ή Ανατολή. Ασφαλές για χρήση από το νήμα και το GUI (lock).
    def __init__(self):
        self.lock = threading.Lock()
        self.reset()

    def reset(self):
        with self.lock:
            self.velocity = [0.0, 0.0]
            self.position = [0.0, 0.0]
            self.path = [(0.0, 0.0)]
            self.distance = 0.0
            self.still = True
            self.bias = [0.0, 0.0]
            self.heading = None
            self.rate = 0.0  # δείγματα ανά δευτερόλεπτο
            self._quiet_since = None
            self._last_time = None

    def update(self, accel, orientation, gyro, heading, now):
        forward, left, up = level_acceleration(accel, orientation)
        linear_g = math.sqrt(forward ** 2 + left ** 2 + up ** 2) / G
        rotation = math.sqrt(gyro["x"] ** 2 + gyro["y"] ** 2 + gyro["z"] ** 2)
        a_up, a_right = to_output_frame(forward, left, heading)
        with self.lock:
            self.heading = heading
            if self._last_time is None:
                self._last_time = now
                return
            dt = now - self._last_time
            self._last_time = now
            if dt <= 0 or dt > 0.5:  # παύση ή πρώτο δείγμα μετά από διακοπή
                return
            self.rate += (1.0 / dt - self.rate) * 0.05

            if linear_g < STILL_ACCEL and rotation < STILL_GYRO:
                if self._quiet_since is None:
                    self._quiet_since = now
            else:
                self._quiet_since = None
            self.still = self._quiet_since is not None and now - self._quiet_since >= STILL_TIME

            if self.still:
                # ZUPT: ταχύτητα 0, και μέτρηση του υπολοίπου για αφαίρεση στην επόμενη κίνηση
                self.velocity = [0.0, 0.0]
                alpha = dt / (BIAS_TAU + dt)
                self.bias[0] += alpha * (a_up - self.bias[0])
                self.bias[1] += alpha * (a_right - self.bias[1])
                return
            for i, a in enumerate((a_up - self.bias[0], a_right - self.bias[1])):
                self.velocity[i] += a * dt
            step = (self.velocity[0] * dt, self.velocity[1] * dt)
            self.position[0] += step[0]
            self.position[1] += step[1]
            self.distance += math.hypot(*step)
            last = self.path[-1]
            if math.hypot(self.position[0] - last[0], self.position[1] - last[1]) >= PATH_STEP:
                self.path.append(tuple(self.position))

    def snapshot(self):
        # Αντίγραφο της κατάστασης για το GUI
        with self.lock:
            return {"path": list(self.path) + [tuple(self.position)], "position": tuple(self.position),
                    "speed": math.hypot(*self.velocity), "distance": self.distance,
                    "still": self.still, "heading": self.heading, "rate": self.rate}


class TrackSampler:
    # Νήμα που διαβάζει τον αισθητήρα (~rate Hz) και τροφοδοτεί τον Tracker. Η ολοκλήρωση
    # χρειάζεται όλα τα δείγματα, γι' αυτό δεν γίνεται στο (αργό) loop του Tk.
    def __init__(self, read_sample, tracker, rate=100.0):
        self.read_sample = read_sample
        self.tracker = tracker
        self.period = 1.0 / rate
        self.error = None
        self._running = False
        self._thread = None

    @property
    def running(self):
        return self._running

    def start(self):
        if self._running:
            return
        self.error = None
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run(self):
        next_time = time.monotonic()
        while self._running:
            try:
                accel, orientation, gyro, heading = self.read_sample()
                self.tracker.update(accel, orientation, gyro, heading, time.monotonic())
            except Exception as e:  # π.χ. σφάλμα I2C: σταματάει και το δείχνει το GUI
                self.error = e
                self._running = False
                return
            next_time += self.period
            delay = next_time - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            else:
                next_time = time.monotonic()


def _nice_step(span):
    # Βήμα πλέγματος 1, 2 ή 5 x 10^k ώστε να φαίνονται ~4-8 γραμμές
    raw = span / 6.0
    power = 10 ** math.floor(math.log10(raw))
    for factor in (1, 2, 5, 10):
        if factor * power >= raw:
            return factor * power
    return 10 * power


def _format_length(meters):
    return f"{meters * 100:g} cm" if meters < 1 else f"{meters:g} m"


class TrackView:
    # Σχεδίαση της διαδρομής σε Tk Canvas με αυτόματη κλίμακα
    def __init__(self, canvas, bg="#1a1a1a"):
        self.canvas = canvas
        self.snapshot = None
        self.message = None  # κείμενο στη μέση του canvas (π.χ. χωρίς Sense HAT)
        canvas.config(bg=bg, highlightthickness=0)
        canvas.bind("<Configure>", lambda event: self.draw())

    def draw(self, snapshot=None):
        if snapshot is not None:
            self.snapshot = snapshot
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 40 or h < 40:
            return
        if self.message:
            c.create_text(w / 2, h / 2, text=self.message, fill="gray70", font="TkDefaultFont 10")
            return
        snap = self.snapshot or {"path": [(0.0, 0.0)], "position": (0.0, 0.0), "heading": None}
        path = snap["path"]

        # Κλίμακα: όλη η διαδρομή (και η αρχή) χωράει, τουλάχιστον 20 cm
        ups = [p[0] for p in path]
        rights = [p[1] for p in path]
        span = max(max(ups) - min(ups), max(rights) - min(rights), 0.2) * 1.25
        center = ((max(ups) + min(ups)) / 2, (max(rights) + min(rights)) / 2)
        margin = 16
        scale = (min(w, h) - 2 * margin) / span

        def to_screen(up, right):
            return w / 2 + (right - center[1]) * scale, h / 2 - (up - center[0]) * scale

        # Πλέγμα με σταθερό βήμα σε μέτρα
        step = _nice_step(span)
        half_w, half_h = w / 2 / scale, h / 2 / scale
        k = math.floor((center[1] - half_w) / step)
        while k * step <= center[1] + half_w:
            x, _ = to_screen(0, k * step)
            c.create_line(x, 0, x, h, fill="gray22")
            k += 1
        k = math.floor((center[0] - half_h) / step)
        while k * step <= center[0] + half_h:
            _, y = to_screen(k * step, 0)
            c.create_line(0, y, w, y, fill="gray22")
            k += 1
        c.create_text(6, h - 6, text=f"grid {_format_length(step)}", anchor="sw", fill="gray60",
                      font="TkDefaultFont 8")

        # Αρχή, διαδρομή, τρέχουσα θέση
        x0, y0 = to_screen(0.0, 0.0)
        c.create_oval(x0 - 4, y0 - 4, x0 + 4, y0 + 4, outline="gray70")
        if len(path) > 1:
            c.create_line(*[v for p in path for v in to_screen(*p)], fill="#40c0ff", width=2)
        x, y = to_screen(*snap["position"])
        c.create_oval(x - 5, y - 5, x + 5, y + 5, fill="yellow", outline="")

        # Προσανατολισμός του γραφήματος: Βορράς πάνω (heading) ή μπροστά πάνω (πλακέτα)
        heading = snap["heading"]
        if heading is None:
            c.create_text(w - 6, 6, text="▲ board forward", anchor="ne", fill="gray60", font="TkDefaultFont 8")
        else:
            c.create_text(w - 6, 6, text="N ▲", anchor="ne", fill="red", font="TkDefaultFont 9 bold")
            # Κατεύθυνση της πλακέτας στο σημείο όπου βρίσκεται
            a = math.radians(heading)
            c.create_line(x, y, x + 18 * math.sin(a), y - 18 * math.cos(a), fill="yellow", width=2,
                          arrow="last", arrowshape=(7, 8, 3))
