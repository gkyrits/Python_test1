"""3D σκηνή γυροσκοπίου με pi3d.

Κάθε module 3D για το pihat_gyro.py δίνει μια κλάση GyroScene με το ίδιο interface:

    scene = GyroScene(width, height, shape_size=(w, h, d), title="")
    image = scene.render(orientation, (width, height))
    scene.close()

- shape_size: διαστάσεις του παραλληλεπιπέδου (μήκος στον X, ύψος κάθετα, βάθος)
- orientation: {"roll", "pitch", "yaw"} σε μοίρες, με τη σύμβαση της Sense HAT
  (X = roll, Y = pitch, Z = yaw)
- render: numpy array (height, width, 3) uint8 RGB, ή None αν η σκηνή έκλεισε
- next_view(): η επόμενη προβολή του σχήματος (VIEWS: "Axes", "Solid"), επιστρέφει το όνομά της
- show_scene(visible): φόντο με φωτογραφία 360° που γυρίζει με τον προσανατολισμό (SceneView)
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
                            GLuint, GLclampf)

# Το παράθυρο του pi3d δεν χρειάζεται (η εικόνα έρχεται από offscreen framebuffer).
# False για να φαίνεται, π.χ. για debug
HIDE_PI3D_WINDOW = True

# Προβολή "Axes" (AxesView)
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


def _empty_node(z=0.0):
    # Γραμμή μηδενικού μήκους: δεν φαίνεται, χρησιμεύει μόνο ως γονέας
    return pi3d.Lines(vertices=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], z=z)


def _line(vertices, width, color):
    line = pi3d.Lines(vertices=vertices, line_width=width, closed=False)
    line.set_material(color)
    return line


class AxesView:
    # Προβολή "Axes": διάφανο σχήμα με ακμές, άξονες X/Y/Z και γράμματα
    # (ρυθμίσεις: *_LINE_WIDTH, *_COLOR, SHAPE_ALPHA)
    name = "Axes"
    background = BACKGROUND_COLOR

    def __init__(self, shape_size):
        # Διαστάσεις: μήκος (pi3d X), ύψος (pi3d Y, κάθετα), βάθος (pi3d Z)
        MY_W, MY_H, MY_D = shape_size

        # Υπολογισμός των μισών αποστάσεων από το κέντρο (extents)
        xw, yh, zd = MY_W / 2.0, MY_H / 2.0, MY_D / 2.0

        self.shader = pi3d.Shader("mat_flat")

        # Cuboid με τις ανεξάρτητες διαστάσεις
        cube = pi3d.Cuboid(w=MY_W, h=MY_H, d=MY_D)
        cube.set_material(SHAPE_COLOR)
        cube.set_alpha(SHAPE_ALPHA)

        # Αόρατος γονέας για ακμές/άξονες/γράμματα: σχεδιάζεται πριν το διάφανο
        # cuboid ώστε οι γραμμές πίσω/μέσα από τις έδρες να μην κόβονται από το depth buffer
        frame = _empty_node()
        self.node = _empty_node()
        self.node.add_child(frame)  # πρώτα οι γραμμές,
        self.node.add_child(cube)   # μετά το διάφανο σώμα

        # Οι 12 ακμές με βάση τα xw, yh, zd
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
            frame.add_child(_line(vertices, EDGE_LINE_WIDTH, EDGE_COLOR))

        # Οι κύριοι άξονες εκτείνονται λίγο πιο έξω από το σώμα του παραλληλεπιπέδου.
        # Ονόματα αξόνων όπως της Sense HAT: X = roll, Y = pitch, Z = yaw.
        # Στο pi3d ο Y είναι ο κάθετος άξονας και ο Z το βάθος, οπότε ο άξονας Y
        # της Sense HAT σχεδιάζεται στο βάθος (pi3d Z) και ο Z κάθετα (pi3d Y)
        Lx, Ly, Lz = xw + 0.4, yh + 0.4, zd + 0.4
        frame.add_child(_line([[0.0, 0.0, 0.0], [Lx, 0.0, 0.0]], AXIS_LINE_WIDTH, AXIS_X_COLOR))
        frame.add_child(_line([[0.0, 0.0, 0.0], [0.0, 0.0, Lz]], AXIS_LINE_WIDTH, AXIS_Y_COLOR))
        frame.add_child(_line([[0.0, 0.0, 0.0], [0.0, Ly, 0.0]], AXIS_LINE_WIDTH, AXIS_Z_COLOR))

        # Τα γράμματα στις άκρες των αξόνων
        labels = (
            # X (στο τέλος του άξονα X)
            (LABEL_X_COLOR, [[[Lx+0.05, 0.05, 0], [Lx+0.15, -0.05, 0]],
                             [[Lx+0.05, -0.05, 0], [Lx+0.15, 0.05, 0]]]),
            # Y (στο τέλος του άξονα Y, στο βάθος)
            (LABEL_Y_COLOR, [[[-0.04, 0.06, Lz+0.05], [0, 0.01, Lz+0.05]],
                             [[0.04, 0.06, Lz+0.05], [0, 0.01, Lz+0.05]],
                             [[0, 0.01, Lz+0.05], [0, -0.04, Lz+0.05]]]),
            # Z (στο τέλος του άξονα Z, πάνω)
            (LABEL_Z_COLOR, [[[-0.04, Ly+0.12, 0], [0.04, Ly+0.12, 0]],
                             [[0.04, Ly+0.12, 0], [-0.04, Ly+0.02, 0]],
                             [[-0.04, Ly+0.02, 0], [0.04, Ly+0.02, 0]]]),
        )
        for color, strokes in labels:
            for vertices in strokes:
                frame.add_child(_line(vertices, LABEL_LINE_WIDTH, color))


# Προβολή "Solid" (SolidView): συμπαγές σχήμα με φωτισμό, χωρίς άξονες.
# Χρώματα (R, G, B) 0.0 - 1.0 όπως φαίνονται (sRGB)
SOLID_BACKGROUND_COLOR = (0.1, 0.1, 0.1, 1.0)  # φόντο (R, G, B, A)
SOLID_TOP_COLOR = (0.96, 0.93, 0.72)          # πάνω επιφάνεια (λευκό-κίτρινο)
SOLID_BOTTOM_COLOR = (0.12, 0.5, 0.2)          # κάτω επιφάνεια (πράσινο)
SOLID_SIDE_COLOR = (0.6, 0.6, 0.6)             # πλαϊνές επιφάνειες (γκρι)
# Φώτα: (κατεύθυνση προς το φως σε pi3d X, Y πάνω, Z βάθος, ένταση/χρώμα)
SOLID_KEY_LIGHT = ((-0.5, 1.0, -0.8), (0.8, 0.78, 0.72))   # κύριο φως, πάνω αριστερά μπροστά
SOLID_FILL_LIGHT = ((0.9, 0.1, -0.3), (0.22, 0.25, 0.32))   # αδύναμο ψυχρό φως από δεξιά
SOLID_SKY_LIGHT = (0.22, 0.24, 0.28)     # ambient για επιφάνειες που κοιτάνε πάνω
SOLID_GROUND_LIGHT = (0.05, 0.05, 0.04)  # ambient για επιφάνειες που κοιτάνε κάτω
SOLID_SPECULAR = 0.35                    # ένταση της γυαλάδας (0 = ματ)
SOLID_SHININESS = 40.0                   # μέγεθος της γυαλάδας (μεγάλο = μικρή, έντονη)

# Shader με φωτισμό ανά pixel (Blinn-Phong) σε συντεταγμένες κόσμου, με gamma 2.2.
# Γράφεται σαν τους shaders του pi3d (#version 120, //precision, //fragcolor)
# και μετατρέπεται για GLES2/GLES3 από το _shader_source
_SOLID_VS = """#version 120
//precision highp float;
attribute vec3 vertex;
attribute vec3 normal;
uniform mat4 modelviewmatrix[3];
varying vec3 normout;
varying vec3 posout;

void main(void) {
  posout = vec3(modelviewmatrix[0] * vec4(vertex, 1.0));
  normout = vec3(modelviewmatrix[0] * vec4(normal, 0.0));
  gl_Position = modelviewmatrix[1] * vec4(vertex, 1.0);
}
"""

_SOLID_FS = """#version 120
//precision highp float;
uniform vec3 unib[5];
uniform vec3 unif[20];
varying vec3 normout;
varying vec3 posout;
//fragcolor

vec3 light(vec3 n, vec3 v, vec3 base, vec3 dir, vec3 color) {
  vec3 l = normalize(dir);
  float diffuse = max(dot(n, l), 0.0);
  float specular = 0.0;
  if (diffuse > 0.0) {
    specular = pow(max(dot(n, normalize(l + v)), 0.0), SHININESS) * SPECULAR;
  }
  return color * (base * diffuse + vec3(specular));
}

void main(void) {
  vec3 base = pow(unib[1], vec3(2.2));    // χρώμα του υλικού, σε γραμμικό χώρο
  vec3 n = normalize(normout);
  vec3 v = normalize(unif[6] - posout);   // προς την κάμερα (unif[6] = eye)
  vec3 color = base * mix(GROUND_LIGHT, SKY_LIGHT, 0.5 + 0.5 * n.y);
  color += light(n, v, base, KEY_DIR, KEY_COLOR);
  color += light(n, v, base, FILL_DIR, FILL_COLOR);
  gl_FragColor = vec4(pow(clamp(color, 0.0, 1.0), vec3(1.0 / 2.2)), unif[5][2]);
}
"""


def _glsl(value):
    # Αριθμός ή tuple σε σταθερά GLSL (float / vec3)
    if isinstance(value, (tuple, list)):
        return "vec3({})".format(", ".join(_glsl(v) for v in value))
    return "{:.6f}".format(value)


def _shader_source(source, vertex):
    # Οι ίδιες αλλαγές που κάνει το pi3d στους δικούς του shaders, ανάλογα με το context
    gl_id = pi3d.Display.Display.INSTANCE.opengl.gl_id
    if gl_id == b"GLES2":
        source = source.replace("//precision", "precision").replace("version 120", "version 100")
    elif gl_id == b"GLES3":
        source = (source.replace("version 120", "version 300 es").replace("//precision", "precision")
                  .replace("attribute", "in").replace("texture2D", "texture")
                  .replace("//fragcolor", "out vec4 fragColor;").replace("gl_FragColor", "fragColor")
                  .replace("varying", "out" if vertex else "in"))
    return source


class SolidView:
    # Προβολή "Solid": συμπαγές σχήμα, κάθε επιφάνεια με το χρώμα της, με φωτισμό
    # (κύριο + δευτερεύον φως, ambient ουρανού/εδάφους, γυαλάδα). Ρυθμίσεις: SOLID_*
    name = "Solid"
    background = SOLID_BACKGROUND_COLOR

    # Οι 6 επιφάνειες του pi3d.Cuboid με τη σειρά τους: +Z, +X, +Y (πάνω), -Y (κάτω), -X, -Z
    FACE_COLORS = (SOLID_SIDE_COLOR, SOLID_SIDE_COLOR, SOLID_TOP_COLOR,
                   SOLID_BOTTOM_COLOR, SOLID_SIDE_COLOR, SOLID_SIDE_COLOR)

    def __init__(self, shape_size):
        constants = {"SHININESS": SOLID_SHININESS, "SPECULAR": SOLID_SPECULAR,
                     "GROUND_LIGHT": SOLID_GROUND_LIGHT, "SKY_LIGHT": SOLID_SKY_LIGHT,
                     "KEY_DIR": SOLID_KEY_LIGHT[0], "KEY_COLOR": SOLID_KEY_LIGHT[1],
                     "FILL_DIR": SOLID_FILL_LIGHT[0], "FILL_COLOR": SOLID_FILL_LIGHT[1]}
        fragment = _SOLID_FS
        for name, value in constants.items():
            fragment = fragment.replace(name, _glsl(value))
        self.shader = pi3d.Shader(vshader_source=_shader_source(_SOLID_VS, True),
                                  fshader_source=_shader_source(fragment, False))

        # Ένα Buffer ανά επιφάνεια ώστε η καθεμιά να έχει το δικό της χρώμα
        MY_W, MY_H, MY_D = shape_size
        body = pi3d.Cuboid(w=MY_W, h=MY_H, d=MY_D)
        body.buf = []
        for face, color in enumerate(self.FACE_COLORS):
            first = 4 * face
            buffer = pi3d.Buffer(body, body.vertices[first:first + 4], body.tex_coords[first:first + 4],
                                 [[i - first for i in triangle] for triangle in body.indices[2 * face:2 * face + 2]],
                                 body.normals[first:first + 4])
            buffer.set_material(color)
            body.buf.append(buffer)

        self.node = _empty_node()
        self.node.add_child(body)


# Οι προβολές με τη σειρά που τις διαλέγει το κουμπί M
VIEWS = (AxesView, SolidView)


# Φόντο "Scene" (SceneView, κουμπί V): φωτογραφία 360° (equirectangular, πλάτος = 2 x ύψος)
# στο εσωτερικό μιας σφαίρας γύρω από την κάμερα, που γυρίζει αντίθετα από την πλακέτα,
# σαν να κοιτάει η κάμερα από την πλακέτα. Χωρίς το αρχείο φτιάχνεται ένα απλό πανόραμα
# (scene_360.jpg: "Kiara 1 Dawn" του Greg Zaal, polyhaven.com, CC0, σε 2048x1024)
SCENE_IMAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scene_360.jpg")
SCENE_TEXTURE_WIDTH = 2048  # πλάτος της υφής σε pixels (ύψος το μισό), όριο για τη GPU του Pi
SCENE_RADIUS = 50.0         # ακτίνα της σφαίρας (πίσω από το σχήμα, μέσα στο far plane)
SCENE_YAW_OFFSET = 0.0      # μοίρες: στροφή της φωτογραφίας ώστε το yaw 0 να κοιτάει όπου θέλουμε
SCENE_DETAIL = (32, 64)     # τμήματα της σφαίρας (κάθετα, οριζόντια)


def _generated_scene(width, height):
    # Πανόραμα χωρίς φωτογραφία: ουρανός, έδαφος, ορίζοντας με N/E/S/W και μοίρες
    from PIL import Image, ImageDraw, ImageFont
    image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(image)
    horizon = height // 2
    for y in range(height):
        if y < horizon:  # ουρανός: σκούρο μπλε πάνω, ανοιχτό στον ορίζοντα
            t = y / horizon
            color = (int(40 + 150 * t), int(80 + 140 * t), int(160 + 90 * t))
        else:            # έδαφος: πράσινο-καφέ, πιο σκούρο προς τα κάτω
            t = (y - horizon) / (height - horizon)
            color = (int(90 - 50 * t), int(110 - 60 * t), int(60 - 30 * t))
        draw.line([(0, y), (width, y)], fill=color)
    try:
        font = ImageFont.load_default(size=height // 12)
    except TypeError:  # Pillow < 10.1
        font = ImageFont.load_default()
    for degrees in range(0, 360, 15):
        x = int(degrees / 360 * width)
        label = {0: "N", 90: "E", 180: "S", 270: "W"}.get(degrees)
        tick = height // 12 if label else height // 40
        draw.line([(x, horizon - tick), (x, horizon + tick)], fill="white", width=3 if label else 1)
        draw.text((x, horizon - tick - 4), label or str(degrees), fill="white",
                  font=font if label else None, anchor="ms")
    return image


def _scene_image():
    from PIL import Image
    width = SCENE_TEXTURE_WIDTH
    try:
        image = Image.open(SCENE_IMAGE).convert("RGB").resize((width, width // 2), Image.LANCZOS)
    except OSError:
        print("Scene photo not found, using a generated panorama:", SCENE_IMAGE)
        image = _generated_scene(width, width // 2)
    # Η ανεστραμμένη σφαίρα του pi3d δείχνει την υφή ανάποδα και σε καθρέφτη
    return image.transpose(Image.ROTATE_180)


class SceneView:
    # Φόντο: σφαίρα με τη φωτογραφία 360°, με gimbal αντίστροφο από αυτό του σχήματος.
    # Ρυθμίσεις: SCENE_*
    def __init__(self):
        self.shader = pi3d.Shader("uv_flat")
        texture = pi3d.Texture(_scene_image(), mipmap=False)
        rings, sides = SCENE_DETAIL
        sphere = pi3d.Sphere(radius=SCENE_RADIUS, slices=rings, sides=sides, invert=True)
        sphere.set_draw_details(self.shader, [texture])

        # Αντίστροφη περιστροφή: (yaw · pitch · roll)⁻¹ = roll⁻¹ · pitch⁻¹ · yaw⁻¹, δηλαδή
        # πρώτα yaw⁻¹ (παιδί), μετά pitch⁻¹, τελευταίο roll⁻¹ (γονέας)
        self.roll_node = _empty_node()
        self.pitch_node = _empty_node()
        self.yaw_node = _empty_node()
        self.roll_node.add_child(self.pitch_node)
        self.pitch_node.add_child(self.yaw_node)
        self.yaw_node.add_child(sphere)

    def draw(self, orientation, camera):
        # Πρόσημα αντίθετα από αυτά του σχήματος στο GyroScene.render
        self.roll_node.rotateToX(orientation['roll'])
        self.pitch_node.rotateToZ(-orientation['pitch'])
        self.yaw_node.rotateToY(-orientation['yaw'] + SCENE_YAW_OFFSET)
        self.roll_node.draw(self.shader, camera=camera)


class GyroScene:
    def __init__(self, width, height, shape_size=(1.6, 0.2, 1.0), title=""):
        # 1. Αρχικοποίηση pi3D Display
        self.pi3d_display = pi3d.Display.create(w=width, h=height, background=BACKGROUND_COLOR,
                                                window_title=title + " (pi3d)")
        self.pi3d_display.resize(x=0, y=self.pi3d_display.max_height, w=width, h=height)
        if HIDE_PI3D_WINDOW:
            self._hide_pi3d_window()

        self.camera = pi3d.Camera()

        # 2. Gimbal: το pi3d εφαρμόζει πάντα Y->X->Z σε ένα Shape, ενώ η Sense HAT
        # θέλει roll->pitch->yaw. Κάθε κόμβος κάνει μία περιστροφή και ο γονέας
        # εφαρμόζεται μετά το παιδί: roll (pi3d X) -> pitch (pi3d Z) -> yaw (pi3d Y) + μετατόπιση
        self.yaw_node = _empty_node(z=3.0)
        self.pitch_node = _empty_node()
        self.roll_node = _empty_node()
        self.yaw_node.add_child(self.pitch_node)
        self.pitch_node.add_child(self.roll_node)

        # 3. Οι προβολές του σχήματος· η τρέχουσα κρέμεται από τον κόμβο roll
        self.views = [view(shape_size) for view in VIEWS]
        self.view_names = [view.name for view in self.views]
        self.set_view(0)

        # Το φόντο 360° (κουμπί V): φτιάχνεται την πρώτη φορά που ζητηθεί
        self.scene = None
        self.scene_visible = False

        # Η σκηνή σχεδιάζεται σε offscreen framebuffer με το μέγεθος που ζητάει το render,
        # ανεξάρτητα από το (κρυφό/ελαχιστοποιημένο) παράθυρο του pi3d
        self.offscreen = None
        self.offscreen_size = None

    def set_view(self, index):
        self.view_index = index % len(self.views)
        self.view = self.views[self.view_index]
        self.roll_node.children = [self.view.node]
        return self.view.name

    def next_view(self):
        # Η επόμενη προβολή (κουμπί M), επιστρέφει το όνομά της
        return self.set_view(self.view_index + 1)

    def show_scene(self, visible):
        # Φόντο 360° πίσω από το σχήμα (κουμπί V)
        if visible and self.scene is None:
            self.scene = SceneView()
        self.scene_visible = visible

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

        pi3d.opengles.glClearColor(*(GLclampf(c) for c in self.view.background))
        self.offscreen.begin()
        if self.scene_visible:
            self.scene.draw(orientation, self.camera)
        self.yaw_node.draw(self.view.shader, camera=self.camera)
        image = self.offscreen.read_pixels()
        self.offscreen.end()
        return image

    def close(self):
        self.pi3d_display.destroy()
