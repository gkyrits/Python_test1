"""3D σκηνή του παιχνιδιού (pi3d): ξύλινη πίστα με τοίχους, τρύπα και μπάλα.

Χρησιμοποιεί το παράθυρο του pi3d που έχει ήδη φτιάξει το pi3d_gyro.GyroScene (το pi3d
δέχεται ένα μόνο Display), το ίδιο offscreen framebuffer και τον ίδιο shader με φωτισμό.

    scene = GameScene()
    scene.set_level(game)            # τοίχοι και τρύπα της πίστας (module game)
    image = scene.render(game, (width, height))
"""
import math

import game as game_rules
from pi3d_gyro import pi3d, GLclampf, ViewFramebuffer, lit_shader, _empty_node

# Χρώματα (R, G, B) 0.0 - 1.0 και θέση της κάμερας
GAME_BACKGROUND_COLOR = (0.1, 0.1, 0.1, 1.0)
GAME_FLOOR_COLOR = (0.78, 0.62, 0.42)   # ανοιχτό ξύλο
GAME_WALL_COLOR = (0.52, 0.34, 0.18)    # σκούρο ξύλο
GAME_HOLE_COLOR = (0.02, 0.02, 0.02)
GAME_BALL_COLOR = (0.82, 0.83, 0.88)    # ατσάλι
GAME_SHADOW_ALPHA = 0.35
GAME_FIT_MARGIN = 1.06      # η απόσταση της κάμερας ώστε να χωράει όλη η πίστα, επί αυτό (περιθώριο)
GAME_BOARD_TILT = 55.0      # μοίρες: πόσο γέρνει η πίστα προς την κάμερα (90 = κάτοψη)
GAME_BOARD_LOWER = 0.3      # πόσο χαμηλότερα από το κέντρο της εικόνας


def _box(x0, z0, x1, z1, y0, y1, color):
    # Κουτί από (x0, y0, z0) ως (x1, y1, z1) σε συντεταγμένες pi3d (y πάνω)
    box = pi3d.Cuboid(w=x1 - x0, h=y1 - y0, d=z1 - z0,
                      x=(x0 + x1) / 2.0, y=(y0 + y1) / 2.0, z=(z0 + z1) / 2.0)
    box.set_material(color)
    return box


class GameScene:
    def __init__(self):
        if pi3d.Display.Display.INSTANCE is None:
            raise RuntimeError("GameScene needs the pi3d display of pi3d_gyro.GyroScene")
        self.display = pi3d.Display.Display.INSTANCE
        self.shader = lit_shader()
        self.camera = pi3d.Camera()

        # Η πίστα: x δεξιά, z μπροστά (το y του παιχνιδιού), y πάνω, γερμένη προς την κάμερα
        self.board = _empty_node()
        self.board.positionY(-GAME_BOARD_LOWER)
        self.board.rotateToX(-GAME_BOARD_TILT)

        hw, hd, t = game_rules.ARENA_WIDTH / 2.0, game_rules.ARENA_DEPTH / 2.0, game_rules.WALL_THICKNESS
        self.board.add_child(_box(-hw - t, -hd - t, hw + t, hd + t, -0.2, 0.0, GAME_FLOOR_COLOR))
        self.hole = pi3d.Disk(radius=game_rules.HOLE_RADIUS, sides=32, y=0.003)
        self.hole.set_material(GAME_HOLE_COLOR)
        self.board.add_child(self.hole)
        self.walls = _empty_node()
        self.board.add_child(self.walls)
        r = game_rules.BALL_RADIUS
        self.ball = pi3d.Sphere(radius=r, slices=16, sides=24)
        self.ball.set_material(GAME_BALL_COLOR)
        self.board.add_child(self.ball)
        # Σκιά κάτω από τη μπάλα (τελευταία, γιατί είναι διάφανη): μικραίνει όσο η μπάλα πηδάει
        self.shadow = pi3d.Disk(radius=r * 0.9, sides=24, y=0.006)
        self.shadow.set_material((0.0, 0.0, 0.0))
        self.shadow.set_alpha(GAME_SHADOW_ALPHA)
        self.board.add_child(self.shadow)

        self.level = None
        self.offscreen = None
        self.offscreen_size = None

    def set_level(self, game):
        # Τοίχοι (περίγραμμα + εσωτερικοί) και τρύπα της πίστας του game
        h = game_rules.WALL_HEIGHT
        self.walls.children = [_box(x0, y0, x1, y1, 0.0, h, GAME_WALL_COLOR)
                               for x0, y0, x1, y1 in game.border + game.walls]
        self.hole.position(game.hole[0], 0.003, game.hole[1])
        self.level = game.level

    def _resize_view(self, w, h):
        if self.offscreen is not None:
            self.offscreen.delete()
            self.offscreen = None
            self.offscreen_size = None
        self.offscreen = ViewFramebuffer(w, h)
        self.offscreen_size = (w, h)
        d = self.display
        self.camera.reset(lens=[d.near, d.far, d.fov, w / float(h)])
        self.board.positionZ(self._fit_distance(w / float(h)))

    def _fit_distance(self, aspect):
        # Απόσταση της πίστας ώστε να χωράει ολόκληρη σε αυτές τις αναλογίες της εικόνας. Η πίστα
        # γέρνει προς την κάμερα: η μπροστινή άκρη είναι πιο κοντά (φαίνεται πιο φαρδιά) και πιο χαμηλά
        tan_v = math.tan(math.radians(self.display.fov / 2.0))
        tan_h = tan_v * aspect
        t = game_rules.WALL_THICKNESS
        half_width = game_rules.ARENA_WIDTH / 2.0 + t
        half_depth = game_rules.ARENA_DEPTH / 2.0 + t
        tilt = math.radians(GAME_BOARD_TILT)
        near = half_depth * math.cos(tilt)                     # πόσο πιο κοντά η μπροστινή άκρη
        drop = half_depth * math.sin(tilt)                     # πόσο πιο χαμηλά / ψηλά οι άκρες
        top = drop - GAME_BOARD_LOWER + game_rules.WALL_HEIGHT  # πάνω άκρη (πίσω τοίχος)
        bottom = drop + GAME_BOARD_LOWER                         # κάτω άκρη (μπροστινή)
        distance = max(half_width / tan_h + near, bottom / tan_v + near, top / tan_v - near)
        return distance * GAME_FIT_MARGIN

    def render(self, game, size):
        if size != self.offscreen_size:
            self._resize_view(*size)
        if game.level != self.level:
            self.set_level(game)

        ball, r = game.ball, game_rules.BALL_RADIUS
        self.ball.position(ball.x, r + ball.h, ball.y)
        falling = game.state in ("falling", "won")
        scale = 0.0 if falling else max(0.3, 1.0 - ball.h / 1.5)
        self.shadow.position(ball.x, 0.006, ball.y)
        self.shadow.scale(scale, 1.0, scale)

        pi3d.opengles.glClearColor(*(GLclampf(c) for c in GAME_BACKGROUND_COLOR))
        self.offscreen.begin()
        self.board.draw(self.shader, camera=self.camera)
        image = self.offscreen.read_pixels()
        self.offscreen.end()
        return image

    def close(self):
        if self.offscreen is not None:
            self.offscreen.delete()
            self.offscreen = None
