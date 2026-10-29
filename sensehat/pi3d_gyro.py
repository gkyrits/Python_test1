"""3D σκηνή γυροσκοπίου με pi3d.

Κάθε module 3D για το pihat_gyro.py δίνει μια κλάση GyroScene με το ίδιο interface:

    scene = GyroScene(width, height, shape_size=(w, h, d), title="")
    image = scene.render(orientation, (width, height))
    scene.close()

- shape_size: διαστάσεις του παραλληλεπιπέδου (μήκος στον X, ύψος κάθετα, βάθος)
- orientation: {"roll", "pitch", "yaw"} σε μοίρες, με τη σύμβαση της Sense HAT
  (X = roll, Y = pitch, Z = yaw)
- render: numpy array (height, width, 3) uint8 RGB, ή None αν η σκηνή έκλεισε
"""
import ctypes
import os
import sys


def _setup_sdl2_angle():
    # Στα Windows το pi3d φτιάχνει desktop OpenGL context μέσω SDL2, αλλά καλεί
    # τις GL συναρτήσεις από το ANGLE libglesv2.dll -> glGetString επιστρέφει None.
    # Ζητάμε από το SDL GLES2 context μέσω EGL (ANGLE) πριν δημιουργηθεί το παράθυρο,
    # και εμποδίζουμε το pi3d να το γυρίσει σε COMPATIBILITY profile.
    import sdl2
    # Το SDL_PollEvent (μέσα στο loop_running) κάνει dispatch ΟΛΑ τα Windows messages
    # του thread, και του Tk, με το GIL ελεύθερο -> Fatal "PyEval_RestoreThread".
    # Τα messages τα μοιράζει μόνο το mainloop του Tk (και στο παράθυρο του SDL).
    sdl2.SDL_SetHint(sdl2.SDL_HINT_WINDOWS_ENABLE_MESSAGELOOP, b"0")
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
    sdl2.SDL_SetHint(sdl2.SDL_HINT_OPENGL_ES_DRIVER, b"1")
    set_attribute = sdl2.SDL_GL_SetAttribute

    def es_set_attribute(attr, value):
        if attr == sdl2.SDL_GL_CONTEXT_PROFILE_MASK:
            value = sdl2.SDL_GL_CONTEXT_PROFILE_ES
        return set_attribute(attr, value)

    sdl2.SDL_GL_SetAttribute = es_set_attribute
    es_set_attribute(sdl2.SDL_GL_CONTEXT_PROFILE_MASK, sdl2.SDL_GL_CONTEXT_PROFILE_ES)
    es_set_attribute(sdl2.SDL_GL_CONTEXT_MAJOR_VERSION, 2)
    es_set_attribute(sdl2.SDL_GL_CONTEXT_MINOR_VERSION, 0)
    es_set_attribute(sdl2.SDL_GL_DEPTH_SIZE, 24)


if sys.platform == "win32":
    # Το pi3d φορτώνει τα ANGLE dll (libEGL/libGLESv2) από τον τρέχοντα φάκελο
    _cwd = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pi3d"))
    try:
        import pi3d
    finally:
        os.chdir(_cwd)
    _setup_sdl2_angle()
else:
    import pi3d
from pi3d.constants import (GL_FRAMEBUFFER, GL_RENDERBUFFER, GL_COLOR_ATTACHMENT0,
                            GL_DEPTH_ATTACHMENT, GL_DEPTH_COMPONENT16, GL_TEXTURE_2D,
                            GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_NEAREST,
                            GL_RGBA, GL_UNSIGNED_BYTE, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
                            GLuint)

# Το παράθυρο του pi3d δεν χρειάζεται (η εικόνα έρχεται από offscreen framebuffer).
# False για να φαίνεται, π.χ. για debug
HIDE_PI3D_WINDOW = True

# Πάχος γραμμών σε pixels (στα Windows το ANGLE σχεδιάζει πάντα 1 pixel)
EDGE_LINE_WIDTH = 2   # ακμές του σχήματος
AXIS_LINE_WIDTH = 2   # άξονες X/Y/Z
LABEL_LINE_WIDTH = 2  # γράμματα X, Y, Z στις άκρες των αξόνων

# Χρώματα (R, G, B) με τιμές 0.0 - 1.0
BACKGROUND_COLOR = (0.1, 0.1, 0.1, 1.0)  # φόντο (R, G, B, A)
SHAPE_COLOR = (0.3, 0.3, 0.3)            # έδρες του σχήματος
SHAPE_ALPHA = 0.3                        # διαφάνεια εδρών (0 διάφανο - 1 συμπαγές)
EDGE_COLOR = (1.0, 1.0, 1.0)             # ακμές του σχήματος
AXIS_X_COLOR = (1.0, 0.0, 0.0)           # άξονας X (κόκκινο)
AXIS_Y_COLOR = (0.0, 1.0, 0.0)           # άξονας Y (πράσινο)
AXIS_Z_COLOR = (0.0, 0.0, 1.0)           # άξονας Z (μπλε)
LABEL_X_COLOR = (1.0, 0.2, 0.2)          # γράμμα X
LABEL_Y_COLOR = (0.2, 1.0, 0.2)          # γράμμα Y
LABEL_Z_COLOR = (0.2, 0.2, 1.0)          # γράμμα Z


class ViewFramebuffer:
    # Offscreen framebuffer (RGBA texture + depth renderbuffer) σταθερού μεγέθους.
    # Το pi3d.OffScreenTexture δεν κάνει: εκτός Pi κολλάει depth texture, που το
    # GLES2 του ANGLE (Windows) δεν υποστηρίζει -> incomplete framebuffer
    def __init__(self, w, h):
        gl = pi3d.opengles
        self.w, self.h = w, h
        self.fbo, self.color, self.depth = GLuint(), GLuint(), GLuint()
        gl.glGenTextures(1, ctypes.byref(self.color))
        gl.glBindTexture(GL_TEXTURE_2D, self.color)
        gl.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        gl.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        gl.glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        gl.glBindTexture(GL_TEXTURE_2D, 0)
        gl.glGenRenderbuffers(1, ctypes.byref(self.depth))
        gl.glBindRenderbuffer(GL_RENDERBUFFER, self.depth)
        gl.glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT16, w, h)
        gl.glBindRenderbuffer(GL_RENDERBUFFER, 0)
        gl.glGenFramebuffers(1, ctypes.byref(self.fbo))
        gl.glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        gl.glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.color, 0)
        gl.glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.depth)
        gl.glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def begin(self):
        gl = pi3d.opengles
        gl.glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        gl.glViewport(0, 0, self.w, self.h)
        gl.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def read_pixels(self):
        return pi3d.masked_screenshot(0, 0, self.w, self.h)

    def end(self):
        pi3d.opengles.glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def delete(self):
        gl = pi3d.opengles
        gl.glDeleteFramebuffers(1, ctypes.byref(self.fbo))
        gl.glDeleteRenderbuffers(1, ctypes.byref(self.depth))
        gl.glDeleteTextures(1, ctypes.byref(self.color))


class GyroScene:
    def __init__(self, width, height, shape_size=(1.6, 0.2, 1.0), title="",
                 background=BACKGROUND_COLOR):
        # Διαστάσεις: μήκος (pi3d X), ύψος (pi3d Y, κάθετα), βάθος (pi3d Z)
        MY_W, MY_H, MY_D = shape_size

        # Υπολογισμός των μισών αποστάσεων από το κέντρο (extents)
        xw, yh, zd = MY_W / 2.0, MY_H / 2.0, MY_D / 2.0

        # 1. Αρχικοποίηση pi3D Display
        self.pi3d_display = pi3d.Display.create(w=width, h=height, background=background,
                                                window_title=title + " (pi3d)")
        self.pi3d_display.resize(x=0, y=self.pi3d_display.max_height, w=width, h=height)
        if HIDE_PI3D_WINDOW:
            self._hide_pi3d_window()

        self.shader = pi3d.Shader("mat_flat")
        self.camera = pi3d.Camera()

        # 2. Δημιουργία του Cuboid με τις ανεξάρτητες διαστάσεις
        self.cube = pi3d.Cuboid(w=MY_W, h=MY_H, d=MY_D)
        self.cube.set_material(SHAPE_COLOR)
        self.cube.set_alpha(SHAPE_ALPHA)

        # Αόρατος γονέας για ακμές/άξονες/γράμματα: σχεδιάζεται πριν το διάφανο
        # cuboid ώστε οι γραμμές πίσω/μέσα από τις έδρες να μην κόβονται από το depth buffer
        self.frame = self._empty_node()

        # Gimbal: το pi3d εφαρμόζει πάντα Y->X->Z σε ένα Shape, ενώ η Sense HAT
        # θέλει roll->pitch->yaw. Κάθε κόμβος κάνει μία περιστροφή και ο γονέας
        # εφαρμόζεται μετά το παιδί: roll (pi3d X) -> pitch (pi3d Z) -> yaw (pi3d Y) + μετατόπιση
        self.yaw_node = self._empty_node(z=3.0)
        self.pitch_node = self._empty_node()
        self.roll_node = self._empty_node()
        self.yaw_node.add_child(self.pitch_node)
        self.pitch_node.add_child(self.roll_node)
        self.roll_node.add_child(self.frame)  # πρώτα οι γραμμές,
        self.roll_node.add_child(self.cube)   # μετά το διάφανο σώμα

        # 3. Αυτόματος υπολογισμός των 12 ακμών με βάση τα xw, yh, zd
        edges_vertices = [
            # Μπροστινό ορθογώνιο (z = -zd)
            [[-xw, -yh, -zd], [xw, -yh, -zd]], [[xw, -yh, -zd], [xw, yh, -zd]],
            [[xw, yh, -zd], [-xw, yh, -zd]], [[-xw, yh, -zd], [-xw, -yh, -zd]],
            # Πίσω ορθογώνιο (z = zd)
            [[-xw, -yh, zd], [xw, -yh, zd]], [[xw, -yh, zd], [xw, yh, zd]],
            [[xw, yh, zd], [-xw, yh, zd]], [[-xw, yh, zd], [-xw, -yh, zd]],
            # Συνδετικές ακμές
            [[-xw, -yh, -zd], [-xw, -yh, zd]], [[xw, -yh, -zd], [xw, -yh, zd]],
            [[xw, yh, -zd], [xw, yh, zd]], [[-xw, yh, -zd], [-xw, yh, zd]]
        ]

        for vertices in edges_vertices:
            edge = pi3d.Lines(vertices=vertices, line_width=EDGE_LINE_WIDTH, closed=False)
            edge.set_material(EDGE_COLOR)
            self.frame.add_child(edge)

        # 4. Σχεδιασμός των Κύριων Αξόνων
        # Οι άξονες εκτείνονται λίγο πιο έξω από το σώμα του παραλληλεπιπέδου
        Lx, Ly, Lz = xw + 0.4, yh + 0.4, zd + 0.4

        axis_x = pi3d.Lines(vertices=[[0.0, 0.0, 0.0], [Lx, 0.0, 0.0]], line_width=AXIS_LINE_WIDTH, closed=False)
        axis_x.set_material(AXIS_X_COLOR)

        # Ονόματα αξόνων όπως της Sense HAT: X = roll, Y = pitch, Z = yaw.
        # Στο pi3d ο Y είναι ο κάθετος άξονας και ο Z το βάθος, οπότε ο άξονας Y
        # της Sense HAT σχεδιάζεται στο βάθος (pi3d Z) και ο Z κάθετα (pi3d Y)
        axis_y = pi3d.Lines(vertices=[[0.0, 0.0, 0.0], [0.0, 0.0, Lz]], line_width=AXIS_LINE_WIDTH, closed=False)
        axis_y.set_material(AXIS_Y_COLOR)

        axis_z = pi3d.Lines(vertices=[[0.0, 0.0, 0.0], [0.0, Ly, 0.0]], line_width=AXIS_LINE_WIDTH, closed=False)
        axis_z.set_material(AXIS_Z_COLOR)

        self.frame.add_child(axis_x)
        self.frame.add_child(axis_y)
        self.frame.add_child(axis_z)

        # 5. Αυτόματη τοποθέτηση των Γραμμάτων (Labels) στις άκρες των αξόνων
        # Γράμμα X (στο τέλος του άξονα X)
        lx1 = pi3d.Lines(vertices=[[Lx+0.05, 0.05, 0], [Lx+0.15, -0.05, 0]], line_width=LABEL_LINE_WIDTH, closed=False)
        lx2 = pi3d.Lines(vertices=[[Lx+0.05, -0.05, 0], [Lx+0.15, 0.05, 0]], line_width=LABEL_LINE_WIDTH, closed=False)
        lx1.set_material(LABEL_X_COLOR)
        lx2.set_material(LABEL_X_COLOR)
        self.frame.add_child(lx1)
        self.frame.add_child(lx2)

        # Γράμμα Y (στο τέλος του άξονα Y, στο βάθος)
        ly1 = pi3d.Lines(vertices=[[-0.04, 0.06, Lz+0.05], [0, 0.01, Lz+0.05]], line_width=LABEL_LINE_WIDTH, closed=False)
        ly2 = pi3d.Lines(vertices=[[0.04, 0.06, Lz+0.05], [0, 0.01, Lz+0.05]], line_width=LABEL_LINE_WIDTH, closed=False)
        ly3 = pi3d.Lines(vertices=[[0, 0.01, Lz+0.05], [0, -0.04, Lz+0.05]], line_width=LABEL_LINE_WIDTH, closed=False)
        ly1.set_material(LABEL_Y_COLOR)
        ly2.set_material(LABEL_Y_COLOR)
        ly3.set_material(LABEL_Y_COLOR)
        self.frame.add_child(ly1)
        self.frame.add_child(ly2)
        self.frame.add_child(ly3)

        # Γράμμα Z (στο τέλος του άξονα Z, πάνω)
        lz1 = pi3d.Lines(vertices=[[-0.04, Ly+0.12, 0], [0.04, Ly+0.12, 0]], line_width=LABEL_LINE_WIDTH, closed=False)
        lz2 = pi3d.Lines(vertices=[[0.04, Ly+0.12, 0], [-0.04, Ly+0.02, 0]], line_width=LABEL_LINE_WIDTH, closed=False)
        lz3 = pi3d.Lines(vertices=[[-0.04, Ly+0.02, 0], [0.04, Ly+0.02, 0]], line_width=LABEL_LINE_WIDTH, closed=False)
        lz1.set_material(LABEL_Z_COLOR)
        lz2.set_material(LABEL_Z_COLOR)
        lz3.set_material(LABEL_Z_COLOR)
        self.frame.add_child(lz1)
        self.frame.add_child(lz2)
        self.frame.add_child(lz3)

        # Η σκηνή σχεδιάζεται σε offscreen framebuffer με το μέγεθος που ζητάει το render,
        # ανεξάρτητα από το (κρυφό/ελαχιστοποιημένο) παράθυρο του pi3d
        self.offscreen = None
        self.offscreen_size = None

    def _hide_pi3d_window(self):
        # Κρύβει το παράθυρο του pi3d: η εικόνα επιστρέφεται από το render
        gl = self.pi3d_display.opengl
        try:
            if pi3d.USE_SDL2:  # Windows (και Linux με SDL2)
                import sdl2
                sdl2.SDL_HideWindow(gl.window)
            elif gl.d is not None:  # Linux / Raspberry Pi με X11: ελαχιστοποίηση
                import ctypes.util
                x11 = ctypes.CDLL(ctypes.util.find_library("X11"))
                x11.XDefaultScreen.argtypes = [ctypes.c_void_p]
                x11.XIconifyWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int]
                x11.XFlush.argtypes = [ctypes.c_void_p]
                d = gl.d if isinstance(gl.d, int) else ctypes.cast(gl.d, ctypes.c_void_p)
                window = gl.window if isinstance(gl.window, int) else gl.window.value
                x11.XIconifyWindow(d, window, x11.XDefaultScreen(d))
                x11.XFlush(d)
        except Exception as e:
            print("Could not hide pi3d window:", e)

    def _resize_view(self, w, h):
        # Το παράθυρο του pi3d δεν αλλάζει μέγεθος (ελαχιστοποιημένο στο X11 δεν
        # αλλάζει ποτέ το buffer του), φτιάχνεται νέο offscreen framebuffer
        d = self.pi3d_display
        if self.offscreen is not None:
            self.offscreen.delete()
        self.offscreen = ViewFramebuffer(w, h)
        self.offscreen_size = (w, h)
        # Νέο aspect ratio στην προβολή ώστε το σχήμα να μην παραμορφώνεται
        self.camera.reset(lens=[d.near, d.far, d.fov, w / float(h)])

    @staticmethod
    def _empty_node(z=0.0):
        # Γραμμή μηδενικού μήκους: δεν φαίνεται, χρησιμεύει μόνο ως γονέας
        return pi3d.Lines(vertices=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], z=z)

    def render(self, orientation, size):
        # Σχεδιάζει το σχήμα με τον δοσμένο προσανατολισμό και επιστρέφει την εικόνα
        if size != self.offscreen_size:
            self._resize_view(*size)
        if not self.pi3d_display.loop_running():
            return None

        # Ο άξονας X του pi3d έχει αντίθετη φορά περιστροφής από το roll της Sense HAT
        self.roll_node.rotateToX(-orientation['roll'])
        self.pitch_node.rotateToZ(orientation['pitch'])
        self.yaw_node.rotateToY(orientation['yaw'])

        self.offscreen.begin()
        self.yaw_node.draw(self.shader, camera=self.camera)
        image = self.offscreen.read_pixels()
        self.offscreen.end()
        return image

    def close(self):
        self.pi3d_display.destroy()
