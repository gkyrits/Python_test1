"""Γραμμική επιτάχυνση: αφαίρεση της βαρύτητας από το επιταχυνσιόμετρο.

Το επιταχυνσιόμετρο μετράει βαρύτητα + πραγματική επιτάχυνση. Μόνο του δεν ξεχωρίζει
κλίση από επιτάχυνση, γι' αυτό η κλίση (roll, pitch) έρχεται από το sense.get_orientation(),
που συνδυάζει gyroscope + accelerometer (fusion του RTIMULib).

    linear = remove_gravity(sense.get_accelerometer_raw(), sense.get_orientation())

Με την πλακέτα ακίνητη το linear είναι ≈ 0 σε X, Y, Z, σε οποιαδήποτε κλίση.
Σφάλμα 1° στον προσανατολισμό αφήνει ~0.017 g βαρύτητας στο αποτέλεσμα.
"""
import math

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
