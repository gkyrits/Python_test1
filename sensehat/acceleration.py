"""Γραμμική επιτάχυνση: αφαίρεση της βαρύτητας από το επιταχυνσιόμετρο.

Το επιταχυνσιόμετρο μετράει βαρύτητα + πραγματική επιτάχυνση. Μόνο του δεν ξεχωρίζει
κλίση από επιτάχυνση, γι' αυτό η κλίση (roll, pitch) έρχεται από το sense.get_orientation(),
που συνδυάζει gyroscope + accelerometer (fusion του RTIMULib).

    linear = remove_gravity(sense.get_accelerometer_raw(), sense.get_orientation())

Με την πλακέτα ακίνητη το linear είναι ≈ 0 σε X, Y, Z, σε οποιαδήποτε κλίση.
Σφάλμα 1° στον προσανατολισμό αφήνει ~0.017 g βαρύτητας στο αποτέλεσμα.

Το υπόλοιπο (offset/κλίμακα του αισθητήρα, καθυστέρηση του fusion) αφαιρείται με το
ResidualCorrection: Zero (μέσος όρος ~1 s με την πλακέτα ακίνητη) ή Auto-zero (αργό φίλτρο).

    correction = ResidualCorrection()
    linear = correction.apply(remove_gravity(...))
"""
import math
import time

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
