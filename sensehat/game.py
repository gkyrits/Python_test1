"""Παιχνίδι λαβύρινθου με κλίση: μπάλα, τοίχοι και τρύπα (φυσική, χωρίς γραφικά).

Η πλακέτα γέρνει και η μπάλα κυλάει προς τα κάτω. Στόχος: να μπει στην τρύπα. Ένα γρήγορο
τίναγμα της πλακέτας προς τα πάνω (δύναμη Z) κάνει τη μπάλα να πηδήξει, και στον αέρα η κλίση
τη μετακινεί ακόμα, οπότε περνάει πάνω από τοίχους.

    game = Game()
    game.update(accel, now)   # accel = sense.get_accelerometer_raw() (g), ή tilt από sliders
    game.ball.x, game.ball.y, game.ball.h, game.state

Συντεταγμένες του επιπέδου: x δεξιά, y μπροστά (μακριά από τον παίκτη), σε μονάδες του
παιχνιδιού (η πίστα είναι ARENA_WIDTH x ARENA_DEPTH με κέντρο το 0, 0). h = ύψος της μπάλας
πάνω από το δάπεδο.
"""
import math
import time

ARENA_WIDTH = 10.0
ARENA_DEPTH = 7.0
BALL_RADIUS = 0.3
HOLE_RADIUS = 0.45
WALL_HEIGHT = 0.5
WALL_THICKNESS = 0.3

# Φυσική (σε μονάδες του παιχνιδιού). Η "βαρύτητα" είναι μικρότερη από την πραγματική
# ώστε η μπάλα να ελέγχεται, όπως σε έναν μικρό ξύλινο λαβύρινθο
GRAVITY = 25.0          # μονάδες/s²
ROLLING = 5.0 / 7.0     # μπάλα που κυλάει: επιτάχυνση = 5/7 · g · sin(κλίση)
DAMPING = 0.6           # 1/s, αντίσταση κύλισης
MAX_SPEED = 12.0        # μονάδες/s
BOUNCE = 0.4            # πόση ταχύτητα κρατάει η μπάλα όταν χτυπάει τοίχο
MAX_STEP = 0.004        # s, μέγιστο βήμα της προσομοίωσης (για να μην περνάει μέσα από τοίχους)

# Άλμα: τίναγμα προς τα πάνω = η Z μέτρηση ξεπερνάει τη μέση τιμή της κατά JUMP_FORCE
JUMP_FORCE = 0.5        # g
JUMP_SPEED = 7.0        # μονάδες/s προς τα πάνω (ύψος ~1.0, ~0.4 s πάνω από WALL_HEIGHT)
JUMP_PUSH = 3.0         # μονάδες/s, ώθηση του άλματος προς την κλίση (πάνω από τοίχους)
JUMP_FULL_TILT = 0.2    # κλίση (sin, ~12°) για όλη την ώθηση· λιγότερη κλίση = μικρότερη ώθηση
JUMP_COOLDOWN = 0.3     # s μετά την προσγείωση πριν από το επόμενο άλμα
Z_TAU = 1.0             # s, μέση τιμή της Z μέτρησης (για την ανίχνευση του τινάγματος)
TILT_TAU = 0.05         # s, εξομάλυνση της κλίσης (θόρυβος του αισθητήρα)

# Κλίση από το επιταχυνσιόμετρο: η μέτρηση σε ηρεμία δείχνει προς τα πάνω (z = +1 g), οπότε
# η μπάλα κυλάει αντίθετα από τις x/y μετρήσεις. Ως (άξονας x=0 / y=1, πρόσημο) για τη
# δεξιά και τη μπροστινή κατεύθυνση της πίστας, με τους άξονες της πλακέτας του Track
# (μπροστά = +y, δεξιά = -x). Αν η μπάλα πάει ανάποδα, αλλάζει το πρόσημο.
RIGHT_TILT = (0, 1.0)
FORWARD_TILT = (1, -1.0)

# Πίστες: start (x, y), hole (x, y), walls (x0, y0, x1, y1). Το περίγραμμα μπαίνει πάντα.
LEVELS = (
    {"start": (-4.0, -2.6), "hole": (4.0, 2.6),
     "walls": ((-0.15, -3.5, 0.15, 1.5),)},
    {"start": (-4.2, 2.8), "hole": (4.2, -2.8),
     "walls": ((-2.7, -1.0, -2.4, 3.5), (-0.15, -3.5, 0.15, 1.0), (2.4, -1.0, 2.7, 3.5))},
    {"start": (-4.0, 0.0), "hole": (3.0, 0.0),
     "walls": ((1.6, -1.4, 1.9, 1.4), (1.6, 1.4, 4.4, 1.7), (1.6, -1.7, 4.4, -1.4),
               (4.1, -1.4, 4.4, 1.4), (-1.5, -3.5, -1.2, -0.6), (-1.5, 0.6, -1.2, 3.5))},
)


class Ball:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = self.vy = 0.0
        self.h = 0.0   # ύψος πάνω από το δάπεδο
        self.vh = 0.0

    @property
    def in_air(self):
        return self.h > 0.0 or self.vh > 0.0


class Game:
    # state: "ready" (πριν την πρώτη κίνηση), "playing", "falling" (μπαίνει στην τρύπα), "won"
    def __init__(self, level=0):
        self.best = {}  # καλύτερος χρόνος ανά πίστα (s), για όσο τρέχει η εφαρμογή
        self.calibration = (0.0, 0.0)  # x/y μέτρηση με την πλακέτα "οριζόντια" (κουμπί C)
        self.start_level(level)

    def start_level(self, level):
        self.level = level % len(LEVELS)
        data = LEVELS[self.level]
        self.hole = data["hole"]
        hw, hd, t = ARENA_WIDTH / 2.0, ARENA_DEPTH / 2.0, WALL_THICKNESS
        # Περίγραμμα: ψηλό για τη φυσική (η μπάλα δεν βγαίνει ούτε με άλμα)
        self.border = ((-hw - t, -hd - t, -hw, hd + t), (hw, -hd - t, hw + t, hd + t),
                       (-hw, -hd - t, hw, -hd), (-hw, hd, hw, hd + t))
        self.walls = tuple(data["walls"])
        self.ball = Ball(*data["start"])
        self.state = "ready"
        self.time = 0.0
        self.tilt = (0.0, 0.0)
        self._z_mean = None
        self._last_time = None
        self._landed_at = -math.inf
        self._fall = 0.0

    def restart(self):
        self.start_level(self.level)

    def next_level(self):
        self.start_level(self.level + 1)

    def pause(self):
        # Το επόμενο update ξεκινάει από εκεί (χωρίς το κενό χρόνο ως βήμα της φυσικής)
        self._last_time = None

    def calibrate(self, accel):
        # Η τωρινή θέση της πλακέτας μετράει ως οριζόντια
        self.calibration = (accel["x"], accel["y"])

    def update(self, accel, now=None, jump=False):
        # accel σε g (x, y, z). jump=True: άλμα χωρίς τίναγμα (κουμπί J)
        now = time.monotonic() if now is None else now
        dt = 0.0 if self._last_time is None else min(now - self._last_time, 0.1)
        self._last_time = now
        reading = (accel["x"] - self.calibration[0], accel["y"] - self.calibration[1])
        target = (RIGHT_TILT[1] * reading[RIGHT_TILT[0]], FORWARD_TILT[1] * reading[FORWARD_TILT[0]])
        k = 1.0 if dt == 0.0 else dt / (TILT_TAU + dt)
        self.tilt = tuple(self.tilt[i] + k * (target[i] - self.tilt[i]) for i in range(2))

        # Τίναγμα προς τα πάνω: Z πάνω από τη μέση τιμή της
        z = accel["z"]
        if self._z_mean is None:
            self._z_mean = z
        flick = z - self._z_mean > JUMP_FORCE
        if not flick:
            self._z_mean += (dt / (Z_TAU + dt)) * (z - self._z_mean) if dt else 0.0
        if (flick or jump) and self.state in ("ready", "playing"):
            self.jump(now)

        if self.state == "ready" and math.hypot(*self.tilt) > 0.05:
            self.state = "playing"
        if self.state in ("playing", "falling"):
            if self.state == "playing":
                self.time += dt
            steps = max(1, math.ceil(dt / MAX_STEP))
            for _ in range(steps):
                if self.state == "won":  # τα υπόλοιπα βήματα θα ξανάρχιζαν την πτώση στην τρύπα
                    break
                self._step(dt / steps, now)

    def jump(self, now=None):
        now = time.monotonic() if now is None else now
        ball = self.ball
        if not ball.in_air and self.state != "falling" and now - self._landed_at >= JUMP_COOLDOWN:
            ball.vh = JUMP_SPEED
            # Ώθηση προς την κατεύθυνση της κλίσης (ανάλογη της κλίσης, ως JUMP_PUSH), ώστε η μπάλα
            # να περνάει πάνω από τοίχο ακόμα κι αν ξεκινάει ακουμπώντας τον
            tilt = math.hypot(*self.tilt)
            if tilt > 0.02:
                push = JUMP_PUSH * min(1.0, tilt / JUMP_FULL_TILT) / tilt
                ball.vx += push * self.tilt[0]
                ball.vy += push * self.tilt[1]
            if self.state == "ready":
                self.state = "playing"

    def _step(self, dt, now):
        ball = self.ball
        if self.state == "falling":
            # Η μπάλα πέφτει μέσα στην τρύπα και κεντράρει
            self._fall += dt
            ball.x += (self.hole[0] - ball.x) * min(1.0, 10.0 * dt)
            ball.y += (self.hole[1] - ball.y) * min(1.0, 10.0 * dt)
            ball.h -= 3.0 * dt
            if self._fall > 0.4:
                self.state = "won"
                best = self.best.get(self.level)
                if best is None or self.time < best:
                    self.best[self.level] = self.time
            return

        # Κύλιση από την κλίση (και στον αέρα, ώστε το άλμα να έχει κατεύθυνση)
        a = GRAVITY * ROLLING
        ball.vx += a * self.tilt[0] * dt
        ball.vy += a * self.tilt[1] * dt
        if not ball.in_air:
            damping = math.exp(-DAMPING * dt)
            ball.vx *= damping
            ball.vy *= damping
        speed = math.hypot(ball.vx, ball.vy)
        if speed > MAX_SPEED:
            ball.vx *= MAX_SPEED / speed
            ball.vy *= MAX_SPEED / speed
        ball.x += ball.vx * dt
        ball.y += ball.vy * dt

        # Άλμα: ύψος με βαρύτητα, προσγείωση στο δάπεδο
        if ball.in_air:
            ball.vh -= GRAVITY * dt
            ball.h += ball.vh * dt
            if ball.h <= 0.0:
                ball.h = ball.vh = 0.0
                self._landed_at = now

        # Τοίχοι: οι εσωτερικοί μόνο όταν η μπάλα δεν είναι πιο ψηλά από αυτούς
        for wall in self.border:
            self._collide(wall)
        if ball.h < WALL_HEIGHT:
            # Όσο η μπάλα ανεβαίνει σε άλμα, ο τοίχος μόνο την κρατάει (δεν αναπηδά), ώστε να κρατήσει
            # την ταχύτητα προς τον τοίχο και να περάσει από πάνω μόλις τον ξεπεράσει σε ύψος
            for wall in self.walls:
                self._collide(wall, bounce=ball.vh <= 0.0)

        # Τρύπα: η μπάλα πέφτει όταν το κέντρο της είναι πάνω από την τρύπα
        if not ball.in_air and math.hypot(ball.x - self.hole[0], ball.y - self.hole[1]) < HOLE_RADIUS - 0.1:
            self.state = "falling"
            self._fall = 0.0

    def _collide(self, wall, bounce=True):
        # Κύκλος (μπάλα) με ορθογώνιο: σπρώχνεται έξω, και η ταχύτητα προς τον τοίχο αναπηδά
        # (bounce=False: η ταχύτητα μένει, μόνο η θέση διορθώνεται)
        ball = self.ball
        x0, y0, x1, y1 = wall
        cx = min(max(ball.x, x0), x1)
        cy = min(max(ball.y, y0), y1)
        dx, dy = ball.x - cx, ball.y - cy
        dist = math.hypot(dx, dy)
        if dist >= BALL_RADIUS:
            return
        if dist < 1e-9:  # το κέντρο μέσα στον τοίχο: έξω από την πιο κοντινή πλευρά
            exits = ((ball.x - x0, -1.0, 0.0), (x1 - ball.x, 1.0, 0.0),
                     (ball.y - y0, 0.0, -1.0), (y1 - ball.y, 0.0, 1.0))
            depth, nx, ny = min(exits)
            push = depth + BALL_RADIUS
        else:
            nx, ny = dx / dist, dy / dist
            push = BALL_RADIUS - dist
        ball.x += nx * push
        ball.y += ny * push
        towards = ball.vx * nx + ball.vy * ny
        if towards < 0.0 and bounce:
            ball.vx -= (1.0 + BOUNCE) * towards * nx
            ball.vy -= (1.0 + BOUNCE) * towards * ny
