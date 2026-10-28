"""Εκτίμηση ταχύτητας και διαδρομής από το επιταχυνσιόμετρο (dead reckoning με ZUPT).

Η γραμμική επιτάχυνση ολοκληρώνεται μία φορά για ταχύτητα και δεύτερη για θέση. Κάθε
μικρό υπόλοιπο σφάλμα μεγαλώνει γρήγορα (0.01 g -> ~5 cm σε 1 s, ~1.2 m σε 5 s), γι' αυτό:
- ZUPT (zero velocity update): όταν η πλακέτα είναι ακίνητη η ταχύτητα γίνεται 0, οπότε
  το σφάλμα μαζεύεται μόνο για τη διάρκεια κάθε κίνησης
- διόρθωση drift σε κάθε στάση: η ταχύτητα που έμεινε τη στιγμή της στάσης είναι το σφάλμα
  της κίνησης, που θεωρείται ότι μεγάλωσε γραμμικά, οπότε διορθώνεται προς τα πίσω όλο το
  κομμάτι της διαδρομής εκείνης της κίνησης
- δική του κλίση (attitude), όχι του RTIMULib: σε κάθε στάση από τον μέσο όρο του
  επιταχυνσιόμετρου (μετράει μόνο βαρύτητα, οπότε η βαρύτητα αφαιρείται ακριβώς, μαζί με
  offset και σφάλμα κλίμακας του αισθητήρα), και στην κίνηση από το gyroscope
- όσο είναι ακίνητη, μετριέται το υπόλοιπο (bias) του gyroscope
- ολοκλήρωση με τραπέζιο (μέσος όρος προηγούμενου και τρέχοντος δείγματος)
Καλά αποτελέσματα: σπρωξίματα σε τραπέζι με στάσεις ανάμεσα. Όχι: συνεχής κίνηση.

    tracker = Tracker()
    tracker.heading_mode = "board" | "gyro" | "compass"
    sampler = TrackSampler(read_sample, tracker)   # νήμα, όσο γρήγορα δίνει δείγματα ο αισθητήρας
    sampler.start() ... sampler.stop()
    view = TrackView(canvas)
    view.draw(tracker.snapshot())

read_sample() επιστρέφει (accel σε g, orientation σε μοίρες, gyro σε rad/s, mag σε µT ή None,
timestamp σε s ή None), όλα με τη σύμβαση της Sense HAT, ή None αν δεν υπάρχει νέο δείγμα.
Το orientation (του RTIMULib) δεν χρησιμοποιείται από τον Tracker: αργεί να συγκλίνει
(π.χ. ~13° λάθος στο Start -> 0.23 g βαρύτητα που δεν αφαιρείται).

Heading (σύστημα αξόνων του γραφήματος):
- board:   άξονες της πλακέτας (πάνω = μπροστά). Η πλακέτα δεν πρέπει να στρίβει.
- gyro:    Βορράς πάνω: αρχική κατεύθυνση από την πυξίδα στο Start, μετά οι στροφές από το
           gyroscope (δεν επηρεάζεται από μέταλλα/μαγνήτες κατά την κίνηση)
- compass: Βορράς πάνω, heading από το μαγνητόμετρο με διόρθωση κλίσης (tilt compensation)
Και στα δύο προστίθεται το heading_offset (το Compass offset της πηγής Raw XY).
"""
import math
import threading
import time
from collections import deque

import numpy as np

G = 9.80665  # m/s² ανά g

# Ανίχνευση ακινησίας (ZUPT), ανεξάρτητη από τα υπόλοιπα (offsets) των αισθητήρων:
# - "σταθερή": σε παράθυρο STILL_TIME η επιτάχυνση και η περιστροφή σχεδόν δεν αλλάζουν
#   (τυπική απόκλιση κάτω από STILL_ACCEL_STD / STILL_GYRO_STD), όσο μεγάλο κι αν είναι το offset
# - ακίνητη = σταθερή ΚΑΙ μικρές τιμές μετά την αφαίρεση των υπολοίπων (STILL_ACCEL / STILL_GYRO),
#   ή σταθερή για πάνω από LONG_STILL (ξαναμαθαίνει υπόλοιπο που άλλαξε, αλλιώς θα κολλούσε σε "Moving")
STILL_TIME = 0.2         # s, παράθυρο για την τυπική απόκλιση
STILL_ACCEL_STD = 0.01   # g
STILL_GYRO_STD = 0.03    # rad/s
STILL_ACCEL = 0.03       # g, μετά την αφαίρεση του υπολοίπου
STILL_GYRO = 0.1         # rad/s (~6°/s), μετά την αφαίρεση του υπολοίπου
LONG_STILL = 1.0         # s
BIAS_TAU = 0.5      # s, σταθερά χρόνου για τη μέτρηση (μέσος όρος) όσο είναι ακίνητη
START_STILL = 1.0   # s μετά το Start/Reset που η πλακέτα θεωρείται ακίνητη (μέτρηση κλίσης,
                    # βαρύτητας και υπολοίπου του gyroscope)
PATH_STEP = 0.002   # m, ελάχιστη απόσταση για νέο σημείο στη διαδρομή
MAX_PATH = 5000     # μέγιστος αριθμός σημείων στη διαδρομή (τα παλαιότερα σβήνονται)

# Αν στην πράξη η διαδρομή βγαίνει καθρεφτισμένη αριστερά/δεξιά, αλλάζει σε -1.0
LEFT_SIGN = 1.0
# Αν στο Gyro heading η διαδρομή στρίβει ανάποδα από την πλακέτα, αλλάζει σε -1.0
YAW_SIGN = 1.0


def level_vector(v, orientation):
    # Διάνυσμα (x, y, z) της πλακέτας στο οριζόντιο σύστημα (μπροστά, πλάι, πάνω):
    # αναιρεί roll και pitch (σύμβαση RTIMULib, Z-Y-X)
    r = math.radians(orientation["roll"])
    p = math.radians(orientation["pitch"])
    vx, vy, vz = v["x"], v["y"], v["z"]
    y1 = vy * math.cos(r) - vz * math.sin(r)
    z1 = vy * math.sin(r) + vz * math.cos(r)
    x2 = vx * math.cos(p) + z1 * math.sin(p)
    z2 = -vx * math.sin(p) + z1 * math.cos(p)
    return x2, y1, z2


def level_acceleration(accel, orientation):
    # Επιτάχυνση (m/s²) σε οριζόντιο σύστημα: x = μπροστά (άξονας X της πλακέτας στο
    # οριζόντιο επίπεδο), y = αριστερά, z = πάνω, χωρίς τη βαρύτητα, ώστε να μη μετράει
    # η κλίση της πλακέτας
    x, y, z = level_vector(accel, orientation)
    return x * G, LEFT_SIGN * y * G, (z - 1.0) * G


def tilt_compensated_heading(mag, orientation):
    # Heading (0..360, δεξιόστροφα από τον Βορρά) από το μαγνητόμετρο, με το πεδίο
    # προβεβλημένο στο οριζόντιο επίπεδο: σωστό και με την πλακέτα γερμένη. Με την
    # πλακέτα οριζόντια δίνει το ίδιο με το compass.raw_heading.
    x, y, _ = level_vector(mag, orientation)
    return (360.0 - math.degrees(math.atan2(y, x))) % 360.0


def to_output_frame(forward, left, heading):
    # (μπροστά, αριστερά) -> (πάνω, δεξιά) στο γράφημα: χωρίς heading οι άξονες της
    # πλακέτας (πάνω = μπροστά), με heading στρέφεται κατά heading μοίρες δεξιόστροφα
    if heading is None:
        return forward, -left
    h = math.radians(heading)
    up = forward * math.cos(h) + left * math.sin(h)
    right = forward * math.sin(h) - left * math.cos(h)
    return up, right


def attitude_from_gravity(a):
    # Πίνακας (πλακέτα -> οριζόντιο σύστημα μπροστά/πλάι/πάνω) από τη μέτρηση της βαρύτητας
    # με την πλακέτα ακίνητη: roll = atan2(y, z), pitch = atan2(-x, sqrt(y² + z²)) όπως στο
    # RTIMULib. Το αποτέλεσμα στέλνει το a ακριβώς στο (0, 0, |a|). Ίδιος με το level_vector.
    r = math.atan2(a[1], a[2])
    p = math.atan2(-a[0], math.hypot(a[1], a[2]))
    cr, sr, cp, sp = math.cos(r), math.sin(r), math.cos(p), math.sin(p)
    return np.array([[cp, sr * sp, cr * sp],
                     [0.0, cr, -sr],
                     [-sp, sr * cp, cr * cp]])


def rotate_by_gyro(attitude, omega, dt):
    # Νέα κλίση μετά από περιστροφή omega (rad/s, άξονες της πλακέτας) για dt (Rodrigues)
    angle = math.sqrt(omega[0] ** 2 + omega[1] ** 2 + omega[2] ** 2) * dt
    if angle < 1e-12:
        return attitude
    k = np.asarray(omega) * dt / angle
    kx = np.array([[0.0, -k[2], k[1]], [k[2], 0.0, -k[0]], [-k[1], k[0], 0.0]])
    rotation = np.eye(3) + math.sin(angle) * kx + (1.0 - math.cos(angle)) * (kx @ kx)
    return attitude @ rotation


def _std(values):
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


class Tracker:
    # Ταχύτητα και θέση στο οριζόντιο επίπεδο (m/s, m): "up" = μπροστά / Βορράς / αρχική
    # κατεύθυνση, "right" = δεξιά. Ασφαλές για χρήση από το νήμα και το GUI (lock).
    def __init__(self):
        self.lock = threading.Lock()
        self.heading_mode = "board"
        self.heading_offset = 0.0  # μοίρες, προστίθεται στο heading της πυξίδας (Compass offset)
        self.reset()

    def reset(self):
        with self.lock:
            self.velocity = [0.0, 0.0]
            self.position = [0.0, 0.0]
            self.path = [(0.0, 0.0, 0.0)]  # (up, right, χρόνος)
            self.distance = 0.0
            self.still = True
            self.gravity = None              # μέσος όρος του επιταχυνσιόμετρου στις στάσεις (g, άξονες πλακέτας)
            self.attitude = np.eye(3)        # πλακέτα -> οριζόντιο σύστημα (μπροστά, πλάι, πάνω)
            self.gyro_bias = [0.0, 0.0, 0.0]  # υπόλοιπο του gyroscope (rad/s), άξονες της πλακέτας
            self._segment_heading = None     # heading στην αρχή της κίνησης
            self.gyro_heading = None     # μοίρες, για heading_mode "gyro" (αρχή από την πυξίδα)
            self.heading = None
            self.rate = 0.0              # δείγματα ανά δευτερόλεπτο
            self.corrections = 0         # πόσες κινήσεις διορθώθηκαν (drift) στις στάσεις
            self._window = deque()       # (χρόνος, μπροστά, αριστερά, πάνω, gx, gy, gz) για STILL_TIME
            self._steady_since = None
            self.diagnostics = {"accel_std": 0.0, "gyro_std": 0.0, "accel": 0.0, "gyro": 0.0}
            self._start_time = None
            self._last_time = None
            self._last_accel = None
            self._segment = None         # κίνηση σε εξέλιξη: χρόνος, δείκτης διαδρομής, απόσταση στην αρχή

    def update(self, accel, orientation, gyro, mag, now):
        acc_b = (accel["x"], accel["y"], accel["z"])
        gyro_raw = (gyro["x"], gyro["y"], gyro["z"])
        with self.lock:
            if self._last_time is None:
                self._last_time = now
                if self._start_time is None:
                    self._start_time = now
                if self.gravity is None:
                    self.gravity = list(acc_b)
                    self.attitude = attitude_from_gravity(acc_b)
                return
            dt = now - self._last_time
            self._last_time = now
            if dt <= 0 or dt > 0.5:  # παύση ή πρώτο δείγμα μετά από διακοπή
                self._last_accel = None
                return
            self.rate += (1.0 / dt - self.rate) * 0.05

            # Gyroscope χωρίς το υπόλοιπο. Στην κίνηση η κλίση ακολουθεί το gyroscope.
            gyro_c = [gyro_raw[i] - self.gyro_bias[i] for i in range(3)]
            if not self.still:
                self.attitude = rotate_by_gyro(self.attitude, gyro_c, dt)
            level = self.attitude @ np.asarray(acc_b)
            g_ref = math.sqrt(sum(v * v for v in self.gravity))
            forward, left, up = level[0] * G, LEFT_SIGN * level[1] * G, (level[2] - g_ref) * G
            yaw_rate = float((self.attitude @ np.asarray(gyro_c))[2])  # γύρω από τον κάθετο άξονα

            # Heading για το σύστημα του γραφήματος. Πυξίδα: μαγνητόμετρο στο οριζόντιο με τη δική
            # μας κλίση, + το Compass offset
            compass_heading = None
            if mag is not None:
                mag_level = self.attitude @ np.array([mag["x"], mag["y"], mag["z"]])
                compass_heading = (360.0 - math.degrees(math.atan2(mag_level[1], mag_level[0]))
                                   + self.heading_offset) % 360.0
            if self.heading_mode == "compass" and compass_heading is not None:
                self.heading = compass_heading
            elif self.heading_mode == "gyro":
                if self.gyro_heading is None:
                    # Αρχική κατεύθυνση από την πυξίδα (αν υπάρχει), μετά μόνο το gyroscope
                    self.gyro_heading = compass_heading if compass_heading is not None else 0.0
                self.gyro_heading -= YAW_SIGN * math.degrees(yaw_rate) * dt
                self.heading = self.gyro_heading % 360.0
            else:
                self.heading = None

            # Ανίχνευση ακινησίας (από τις τιμές του αισθητήρα, ανεξάρτητα από offsets)
            self._window.append((now,) + acc_b + gyro_raw)
            while self._window and self._window[0][0] < now - STILL_TIME:
                self._window.popleft()
            full = self._window[-1][0] - self._window[0][0] >= STILL_TIME * 0.8
            accel_std = max(_std([w[i] for w in self._window]) for i in (1, 2, 3))
            gyro_std = max(_std([w[i] for w in self._window]) for i in (4, 5, 6))
            accel_g = math.sqrt(forward ** 2 + left ** 2 + up ** 2) / G
            gyro_abs = math.sqrt(sum(g * g for g in gyro_c))
            self.diagnostics = {"accel_std": accel_std, "gyro_std": gyro_std, "accel": accel_g, "gyro": gyro_abs}
            steady = full and accel_std < STILL_ACCEL_STD and gyro_std < STILL_GYRO_STD
            if steady:
                if self._steady_since is None:
                    self._steady_since = now
            else:
                self._steady_since = None
            small = accel_g < STILL_ACCEL and gyro_abs < STILL_GYRO
            was_still = self.still
            self.still = ((steady and small) or (steady and now - self._steady_since >= LONG_STILL)
                          or now - self._start_time < START_STILL)

            if self.still:
                if not was_still:
                    self._correct_segment(now)
                # ZUPT: ταχύτητα 0. Μέσος όρος βαρύτητας -> κλίση (η βαρύτητα αφαιρείται ακριβώς),
                # και υπόλοιπο του gyroscope.
                self.velocity = [0.0, 0.0]
                alpha = dt / (BIAS_TAU + dt)
                for i in range(3):
                    self.gravity[i] += alpha * (acc_b[i] - self.gravity[i])
                    self.gyro_bias[i] += alpha * (gyro_raw[i] - self.gyro_bias[i])
                self.attitude = attitude_from_gravity(self.gravity)
                self._last_accel = None
                return

            if was_still:
                # Αρχή κίνησης: ξεκινάει ένα κομμάτι διαδρομής για διόρθωση στην επόμενη στάση. Η κλίση
                # από εδώ ακολουθεί το gyroscope ως προς την κατεύθυνση της πλακέτας τώρα, οπότε το
                # γράφημα στρέφεται κατά το heading αυτής της στιγμής.
                self._segment = (now - dt, len(self.path), self.distance)
                self._segment_heading = self.heading
            accel_now = to_output_frame(forward, left, self._segment_heading)
            accel_prev = self._last_accel or accel_now
            self._last_accel = accel_now
            step = [0.0, 0.0]
            for i in range(2):
                v_prev = self.velocity[i]
                self.velocity[i] += (accel_prev[i] + accel_now[i]) / 2.0 * dt  # τραπέζιο
                step[i] = (v_prev + self.velocity[i]) / 2.0 * dt
            self.position[0] += step[0]
            self.position[1] += step[1]
            self.distance += math.hypot(*step)
            last = self.path[-1]
            if math.hypot(self.position[0] - last[0], self.position[1] - last[1]) >= PATH_STEP:
                self._add_point(now)

    def _add_point(self, now):
        self.path.append((self.position[0], self.position[1], now))
        if len(self.path) > MAX_PATH:
            del self.path[0]
            if self._segment is not None:
                start_time, start_index, start_distance = self._segment
                self._segment = (start_time, max(0, start_index - 1), start_distance)

    def _correct_segment(self, now):
        # Στάση: η ταχύτητα που έμεινε είναι το σφάλμα της κίνησης. Αν μεγάλωσε γραμμικά από
        # την αρχή της κίνησης (σταθερό υπόλοιπο επιτάχυνσης), το σφάλμα θέσης τη στιγμή t
        # είναι v_err * (t - t0)² / (2T). Αφαιρείται από κάθε σημείο της κίνησης.
        if self._segment is None:
            return
        start_time, start_index, start_distance = self._segment
        self._segment = None
        duration = now - start_time
        if duration <= 0:
            return
        v_err = list(self.velocity)

        def corrected(up, right, t):
            k = (t - start_time) ** 2 / (2.0 * duration)
            return up - v_err[0] * k, right - v_err[1] * k

        for i in range(start_index, len(self.path)):
            up, right, t = self.path[i]
            self.path[i] = corrected(up, right, t) + (t,)
        self.position = list(corrected(self.position[0], self.position[1], now))
        self._add_point(now)
        # Απόσταση της κίνησης από τα διορθωμένα σημεία
        distance = start_distance
        for i in range(max(start_index, 1), len(self.path)):
            distance += math.hypot(self.path[i][0] - self.path[i - 1][0], self.path[i][1] - self.path[i - 1][1])
        self.distance = distance
        self.corrections += 1

    def snapshot(self):
        # Αντίγραφο της κατάστασης για το GUI
        with self.lock:
            return {"path": [(p[0], p[1]) for p in self.path] + [tuple(self.position)],
                    "position": tuple(self.position), "speed": math.hypot(*self.velocity),
                    "distance": self.distance, "still": self.still, "heading": self.heading,
                    "heading_mode": self.heading_mode, "rate": self.rate,
                    "corrections": self.corrections, "diagnostics": dict(self.diagnostics)}


class TrackSampler:
    # Νήμα που διαβάζει τον αισθητήρα και τροφοδοτεί τον Tracker. Η ολοκλήρωση χρειάζεται
    # όλα τα δείγματα, γι' αυτό δεν γίνεται στο (αργό) loop του Tk. Όταν το read_sample
    # επιστρέφει None (κανένα νέο δείγμα), περιμένει poll δευτερόλεπτα και ξαναδοκιμάζει.
    def __init__(self, read_sample, tracker, poll=0.002):
        self.read_sample = read_sample
        self.tracker = tracker
        self.poll = poll
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
        while self._running:
            try:
                sample = self.read_sample()
                if sample is None:
                    time.sleep(self.poll)
                    continue
                accel, orientation, gyro, mag, timestamp = sample
                now = time.monotonic() if timestamp is None else timestamp
                self.tracker.update(accel, orientation, gyro, mag, now)
            except Exception as e:  # π.χ. σφάλμα I2C: σταματάει και το δείχνει το GUI
                self.error = e
                self._running = False
                return


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
        # Διάγνωση της ανίχνευσης ακινησίας: απόκλιση (σ) και τιμές χωρίς υπόλοιπο, με τα όρια.
        # Πορτοκαλί η τιμή που κρατάει την πλακέτα σε "Moving" όταν είναι πάνω από το όριο.
        diag = snap.get("diagnostics")
        if diag:
            items = (("σa", diag["accel_std"], STILL_ACCEL_STD, "g", 3), ("σω", diag["gyro_std"], STILL_GYRO_STD, "", 3),
                     ("|a|", diag["accel"], STILL_ACCEL, "g", 3), ("|ω|", diag["gyro"], STILL_GYRO, "", 2))
            for row, (name, value, limit, unit, digits) in enumerate(items):
                c.create_text(6, 6 + row * 12, text=f"{name} {value:.{digits}f}/{limit:g}{unit}", anchor="nw",
                              fill="#d07000" if value >= limit else "gray60", font="TkDefaultFont 8")
            c.create_text(6, 6 + 4 * 12, text=f"{snap.get('rate', 0):.0f} Hz", anchor="nw", fill="gray60",
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
        mode = snap.get("heading_mode", "board")
        if heading is None:
            c.create_text(w - 6, 6, text="▲ board forward", anchor="ne", fill="gray60", font="TkDefaultFont 8")
        else:
            label = "N ▲ (gyro)" if mode == "gyro" else "N ▲"
            c.create_text(w - 6, 6, text=label, anchor="ne", fill="red", font="TkDefaultFont 9 bold")
            # Κατεύθυνση της πλακέτας στο σημείο όπου βρίσκεται
            a = math.radians(heading)
            c.create_line(x, y, x + 18 * math.sin(a), y - 18 * math.cos(a), fill="yellow", width=2,
                          arrow="last", arrowshape=(7, 8, 3))
