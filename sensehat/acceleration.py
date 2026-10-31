"""Γραμμική επιτάχυνση: αφαίρεση της βαρύτητας από το επιταχυνσιόμετρο.

Το επιταχυνσιόμετρο μετράει βαρύτητα + πραγματική επιτάχυνση. Μόνο του δεν ξεχωρίζει
κλίση από επιτάχυνση. Δύο τρόποι:

- GravityTracker (Linear στο Accelerometer tab): δική του κλίση, όπως το Track. Στις στάσεις
  η βαρύτητα είναι ακριβώς η μέτρηση (μέσος όρος), στην κίνηση την ακολουθεί το gyroscope.
  Δεν περιμένει το fusion του RTIMULib να ηρεμήσει, και η βαθμονόμηση (|g| ≠ 1) δεν πειράζει.

    tracker = GravityTracker()
    linear = tracker.update(sense.get_accelerometer_raw(), sense.get_gyroscope_raw())

- remove_gravity: με την κλίση (roll, pitch) από το sense.get_orientation() (fusion του
  RTIMULib). Σφάλμα 1° στον προσανατολισμό αφήνει ~0.017 g βαρύτητας στο αποτέλεσμα.

    linear = remove_gravity(sense.get_accelerometer_raw(), sense.get_orientation())

Με την πλακέτα ακίνητη το linear είναι ≈ 0 σε X, Y, Z, σε οποιαδήποτε κλίση.

Το υπόλοιπο (offset/κλίμακα του αισθητήρα, καθυστέρηση του fusion) αφαιρείται με το
ResidualCorrection: Zero (μέσος όρος ~1 s με την πλακέτα ακίνητη) ή Auto-zero (αργό φίλτρο).

    correction = ResidualCorrection()
    linear = correction.apply(tracker.update(...))
"""
import math
import time
from collections import deque

AXES = ("x", "y", "z")

# Πρόσημο της βαρύτητας ανά άξονα. Αν σε ηρεμία ένας άξονας του linear μεγαλώνει
# όταν γέρνει η πλακέτα (αντί να μένει ≈ 0), αλλάζει το πρόσημο εκείνου του άξονα σε -1.0
GRAVITY_SIGNS = {"x": 1.0, "y": 1.0, "z": 1.0}


def gravity_vector(orientation):
    # Η βαρύτητα (σε g) όπως τη μετράει το επιταχυνσιόμετρο στους άξονες της πλακέτας,
    # για roll/pitch σε μοίρες (σύμβαση RTIMULib, Z-Y-X). Το yaw δεν επηρεάζει.
    # Οριζόντια πλακέτα: (0, 0, 1). Ίδια σύμβαση με τον υπολογισμό κλίσης του RTIMULib:
    # roll = atan2(y, z), pitch = atan2(-x, sqrt(y² + z²))
    r = math.radians(orientation["roll"])
    p = math.radians(orientation["pitch"])
    gravity = {"x": -math.sin(p), "y": math.sin(r) * math.cos(p), "z": math.cos(r) * math.cos(p)}
    return {axis: GRAVITY_SIGNS[axis] * gravity[axis] for axis in AXES}


def remove_gravity(accel, orientation):
    # Γραμμική επιτάχυνση (g) = μέτρηση - βαρύτητα, και στους τρεις άξονες
    gravity = gravity_vector(orientation)
    return {axis: accel[axis] - gravity[axis] for axis in AXES}


# Ακινησία για το GravityTracker (ίδια λογική με το track.py): σε παράθυρο STILL_TIME η
# επιτάχυνση και η περιστροφή σχεδόν δεν αλλάζουν, όσο μεγάλο κι αν είναι το offset
STILL_TIME = 0.3        # s
STILL_ACCEL_STD = 0.01  # g
STILL_GYRO_STD = 0.03   # rad/s
GRAVITY_TAU = 0.3       # s, μέσος όρος της βαρύτητας και του υπολοίπου του gyroscope σε ηρεμία
MAX_GAP = 0.5           # s, μεγαλύτερο κενό ανάμεσα σε δείγματα = νέα αρχή (π.χ. αλλαγή tab)


def _std(values):
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def rotate_into_body(vector, omega, dt):
    # Ένα σταθερό διάνυσμα (π.χ. η βαρύτητα) στους άξονες της πλακέτας, αφού η πλακέτα
    # περιστράφηκε με omega (rad/s, άξονες πλακέτας) για dt: περιστροφή κατά -omega·dt (Rodrigues).
    # Ίδια σύμβαση με το track.rotate_by_gyro, που ελέγχθηκε στο Pi
    angle = math.sqrt(sum(w * w for w in omega)) * dt
    if angle < 1e-12:
        return list(vector)
    k = [w * dt / angle for w in omega]
    v = vector
    cross = (k[1] * v[2] - k[2] * v[1], k[2] * v[0] - k[0] * v[2], k[0] * v[1] - k[1] * v[0])
    dot = sum(k[i] * v[i] for i in range(3))
    c, s = math.cos(angle), math.sin(angle)
    return [v[i] * c - cross[i] * s + k[i] * dot * (1.0 - c) for i in range(3)]


class GravityTracker:
    # Γραμμική επιτάχυνση με δική του κλίση: η βαρύτητα στους άξονες της πλακέτας μετριέται
    # όσο η πλακέτα είναι ακίνητη (μέσος όρος της μέτρησης) και στην κίνηση γυρίζει με το
    # gyroscope (χωρίς το υπόλοιπό του, που μετριέται κι αυτό στις στάσεις).
    # Σταθερή επιτάχυνση χωρίς καμία αλλαγή για πάνω από STILL_TIME μοιάζει με ακινησία
    # και αφαιρείται σαν βαρύτητα.
    def __init__(self):
        self.reset()

    def reset(self):
        self.gravity = None              # g, άξονες της πλακέτας
        self.gyro_bias = [0.0, 0.0, 0.0]  # rad/s
        self.still = True
        self._window = deque()           # (χρόνος, ax, ay, az, gx, gy, gz)
        self._last_time = None

    def update(self, accel, gyro, now=None):
        # accel σε g, gyro σε rad/s (sense.get_accelerometer_raw / get_gyroscope_raw)
        now = time.monotonic() if now is None else now
        a = [accel[axis] for axis in AXES]
        w = [gyro[axis] for axis in AXES]
        dt = None if self._last_time is None else now - self._last_time
        self._last_time = now
        if self.gravity is None or dt is None or dt <= 0 or dt > MAX_GAP:
            # Αρχή (ή μετά από κενό): η πλακέτα θεωρείται ακίνητη μέχρι να γεμίσει το παράθυρο
            self.gravity = list(a)
            self._window.clear()
            dt = 0.0

        self._window.append([now] + a + w)
        while self._window[0][0] < now - STILL_TIME:
            self._window.popleft()
        full = self._window[-1][0] - self._window[0][0] >= STILL_TIME * 0.8
        steady = (full and max(_std([s[i] for s in self._window]) for i in (1, 2, 3)) < STILL_ACCEL_STD
                  and max(_std([s[i] for s in self._window]) for i in (4, 5, 6)) < STILL_GYRO_STD)
        self.still = steady or not full

        if self.still:
            alpha = 1.0 if dt == 0.0 else dt / (GRAVITY_TAU + dt)
            for i in range(3):
                self.gravity[i] += alpha * (a[i] - self.gravity[i])
                if dt > 0.0:
                    self.gyro_bias[i] += alpha * (w[i] - self.gyro_bias[i])
        else:
            omega = [w[i] - self.gyro_bias[i] for i in range(3)]
            self.gravity = rotate_into_body(self.gravity, omega, dt)
        return {axis: a[i] - self.gravity[i] for i, axis in enumerate(AXES)}


class GravityCheck:
    # Έλεγχος βαθμονόμησης: με την πλακέτα ακίνητη το επιταχυνσιόμετρο μετράει μόνο τη
    # βαρύτητα, άρα |a| ≈ 1 g σε κάθε θέση. Αν διαφέρει πάνω από tolerance (π.χ. 0.42 g από
    # λάθος AccelCalMin/Max στο RTIMULib.ini), ok = False. Κρίνεται μόνο όταν η πλακέτα είναι
    # ακίνητη (μικρή απόκλιση του |a| στα τελευταία window δείγματα), αλλιώς κρατάει το προηγούμενο.
    def __init__(self, tolerance=0.1, window=10, steady_std=0.01):
        self.tolerance = tolerance
        self.window = window
        self.steady_std = steady_std
        self.ok = True
        self.magnitude = None  # μέσος όρος |a| (g) την τελευταία φορά που ήταν ακίνητη
        self._values = []

    def update(self, accel):
        self._values.append(math.sqrt(sum(accel[axis] ** 2 for axis in AXES)))
        if len(self._values) > self.window:
            del self._values[0]
        if len(self._values) < self.window:
            return self.ok
        mean = sum(self._values) / len(self._values)
        std = math.sqrt(sum((v - mean) ** 2 for v in self._values) / len(self._values))
        if std < self.steady_std:
            self.magnitude = mean
            self.ok = abs(mean - 1.0) <= self.tolerance
        return self.ok

    def reset(self):
        self.ok = True
        self.magnitude = None
        self._values = []


class ResidualCorrection:
    # Αφαιρεί το υπόλοιπο (bias) που μένει στη γραμμική επιτάχυνση με την πλακέτα ακίνητη.
    # - start_zero(): μέσος όρος για zero_time δευτερόλεπτα -> bias (η πλακέτα πρέπει να μένει ακίνητη)
    # - auto = True: το bias ακολουθεί αργά (σταθερά χρόνου auto_tau) ό,τι μένει σταθερό, άρα
    #   χτυπήματα/ωθήσεις φαίνονται κανονικά, αλλά σταθερή επιτάχυνση εξαφανίζεται σιγά σιγά
    def __init__(self, zero_time=1.0, auto_tau=2.0):
        self.zero_time = zero_time
        self.auto_tau = auto_tau
        self.auto = False
        self.bias = {axis: 0.0 for axis in AXES}
        self._zero_samples = None  # δείγματα όσο γίνεται το Zero
        self._zero_end = 0.0
        self._last_time = None

    @property
    def zeroing(self):
        return self._zero_samples is not None

    def start_zero(self):
        self._zero_samples = []
        self._zero_end = time.monotonic() + self.zero_time

    def reset(self):
        self.bias = {axis: 0.0 for axis in AXES}
        self._zero_samples = None
        self._last_time = None

    def apply(self, linear, now=None):
        # Διορθωμένη τιμή = linear - bias. Ενημερώνει το bias από το Zero ή το Auto-zero.
        now = time.monotonic() if now is None else now
        if self._zero_samples is not None:
            self._zero_samples.append(linear)
            if now >= self._zero_end:
                samples, self._zero_samples = self._zero_samples, None
                self.bias = {axis: sum(s[axis] for s in samples) / len(samples) for axis in AXES}
        elif self.auto and self._last_time is not None:
            dt = max(0.0, now - self._last_time)
            alpha = dt / (self.auto_tau + dt)
            for axis in AXES:
                self.bias[axis] += alpha * (linear[axis] - self.bias[axis])
        self._last_time = now
        return {axis: linear[axis] - self.bias[axis] for axis in AXES}
