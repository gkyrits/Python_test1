import ctypes
import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

try:
    from sense_hat import SenseHat
except ImportError:
    try:
        from sense_emu import SenseHat
    except ImportError:
        SenseHat = None


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

WINDOW_TITLE = "Sense Gyroscope"
# Αν το Tk δείχνει μαύρη εικόνα με κρυφό παράθυρο pi3d, κάντε το False
HIDE_PI3D_WINDOW = True

CANVAS_BG_COLOR = "light gray"
CANVAS_WIDTH = 350
CANVAS_HEIGHT = 250


class Transparent3DCubeApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WINDOW_TITLE)
        
        if SenseHat is not None:
            self.sense = SenseHat()
            self.sense.clear()
        else:
            self.sense = None
        self.sensor = None  # τελευταία ανάγνωση του αισθητήρα (για το calibrate)

        # 1. ΟΡΙΣΤΕ ΕΔΩ ΤΙΣ ΑΝΕΞΑΡΤΗΤΕΣ ΔΙΑΣΤΑΣΕΙΣ (Width, Height, Depth)
        MY_W = 1.6  # Μήκος (Άξονας X)
        MY_H = 0.2  # Ύψος (Άξονας Y)
        MY_D = 1.0  # Βάθος (Άξονας Z)
        
        # Υπολογισμός των μισών αποστάσεων από το κέντρο (extents)
        xw, yh, zd = MY_W / 2.0, MY_H / 2.0, MY_D / 2.0
        
        # 2. Αρχικοποίηση pi3D Display
        self.pi3d_display = pi3d.Display.create(w=CANVAS_WIDTH, h=CANVAS_HEIGHT, background=(0.1, 0.1, 0.1, 1.0),
                                                window_title=WINDOW_TITLE+ " (pi3d)")
        self.pi3d_display.resize(x=0, y=self.pi3d_display.max_height, w=CANVAS_WIDTH, h=CANVAS_HEIGHT)
        if HIDE_PI3D_WINDOW:
            self._hide_pi3d_window()
        
        self.shader = pi3d.Shader("mat_flat")
        self.camera = pi3d.Camera()

        # 3. Δημιουργία του Cuboid με τις ανεξάρτητες διαστάσεις
        self.cube = pi3d.Cuboid(w=MY_W, h=MY_H, d=MY_D)
        self.cube.set_material((0.3, 0.3, 0.3))
        self.cube.set_alpha(0.3)

        # Αόρατος γονέας για ακμές/άξονες/γράμματα: σχεδιάζεται πριν το διάφανο
        # cuboid ώστε οι γραμμές πίσω/μέσα από τις έδρες να μην κόβονται από το depth buffer
        self.frame = self._empty_node()

        # Gimbal: το pi3d εφαρμόζει πάντα Y->X->Z σε ένα Shape, ενώ η Sense HAT
        # θέλει roll->pitch->yaw. Κάθε κόμβος κάνει μία περιστροφή και ο γονέας
        # εφαρμόζεται μετά το παιδί: roll (X) -> pitch (Z) -> yaw (Y) + μετατόπιση
        self.yaw_node = self._empty_node(z=3.0)
        self.pitch_node = self._empty_node()
        self.roll_node = self._empty_node()
        self.yaw_node.add_child(self.pitch_node)
        self.pitch_node.add_child(self.roll_node)
        self.roll_node.add_child(self.frame)  # πρώτα οι γραμμές,
        self.roll_node.add_child(self.cube)   # μετά το διάφανο σώμα

        # 4. Αυτόματος υπολογισμός των 12 ακμών με βάση τα xw, yh, zd
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
            edge = pi3d.Lines(vertices=vertices, line_width=3, closed=False)
            edge.set_material((1.0, 1.0, 1.0))
            self.frame.add_child(edge)
        
        # 5. Σχεδιασμός των Κύριων Αξόνων
        # Οι άξονες εκτείνονται λίγο πιο έξω από το σώμα του παραλληλεπιπέδου
        Lx, Ly, Lz = xw + 0.4, yh + 0.4, zd + 0.4
        
        axis_x = pi3d.Lines(vertices=[[0.0, 0.0, 0.0], [Lx, 0.0, 0.0]], line_width=4, closed=False)
        axis_x.set_material((1.0, 0.0, 0.0)) # Κόκκινο
        
        axis_y = pi3d.Lines(vertices=[[0.0, 0.0, 0.0], [0.0, Ly, 0.0]], line_width=4, closed=False)
        axis_y.set_material((0.0, 1.0, 0.0)) # Πράσινο
        
        axis_z = pi3d.Lines(vertices=[[0.0, 0.0, 0.0], [0.0, 0.0, Lz]], line_width=4, closed=False)
        axis_z.set_material((0.0, 0.0, 1.0)) # Μπλε
        
        self.frame.add_child(axis_x)
        self.frame.add_child(axis_y)
        self.frame.add_child(axis_z)
        
        # 6. Αυτόματη τοποθέτηση των Γραμμάτων (Labels) στις άκρες των αξόνων
        # Γράμμα X (στο τέλος του άξονα X)
        lx1 = pi3d.Lines(vertices=[[Lx+0.05, 0.05, 0], [Lx+0.15, -0.05, 0]], line_width=3, closed=False)
        lx2 = pi3d.Lines(vertices=[[Lx+0.05, -0.05, 0], [Lx+0.15, 0.05, 0]], line_width=3, closed=False)
        lx1.set_material((1.0, 0.2, 0.2))
        lx2.set_material((1.0, 0.2, 0.2))
        self.frame.add_child(lx1)
        self.frame.add_child(lx2)
        
        # Γράμμα Y (στο τέλος του άξονα Y)
        ly1 = pi3d.Lines(vertices=[[-0.04, Ly+0.12, 0], [0, Ly+0.07, 0]], line_width=3, closed=False)
        ly2 = pi3d.Lines(vertices=[[0.04, Ly+0.12, 0], [0, Ly+0.07, 0]], line_width=3, closed=False)
        ly3 = pi3d.Lines(vertices=[[0, Ly+0.07, 0], [0, Ly+0.02, 0]], line_width=3, closed=False)
        ly1.set_material((0.2, 1.0, 0.2))
        ly2.set_material((0.2, 1.0, 0.2))
        ly3.set_material((0.2, 1.0, 0.2))
        self.frame.add_child(ly1)
        self.frame.add_child(ly2)
        self.frame.add_child(ly3)
        
        # Γράμμα Z (στο τέλος του άξονα Z)
        lz1 = pi3d.Lines(vertices=[[-0.04, 0.04, Lz+0.05], [0.04, 0.04, Lz+0.05]], line_width=3, closed=False)
        lz2 = pi3d.Lines(vertices=[[0.04, 0.04, Lz+0.05], [-0.04, -0.04, Lz+0.05]], line_width=3, closed=False)
        lz3 = pi3d.Lines(vertices=[[-0.04, -0.04, Lz+0.05], [0.04, -0.04, Lz+0.05]], line_width=3, closed=False)
        lz1.set_material((0.2, 0.2, 1.0))
        lz2.set_material((0.2, 0.2, 1.0))
        lz3.set_material((0.2, 0.2, 1.0))
        self.frame.add_child(lz1)
        self.frame.add_child(lz2)
        self.frame.add_child(lz3)
        
        # 7. Στήσιμο του Tkinter GUI Canvas
        # Ο canvas ακολουθεί το μέγεθος του παραθύρου, και το pi3d display τον canvas
        # shape_frame: αριστερά το tool_frame με τα κουμπιά, δεξιά ο canvas
        # (pack στο τέλος, μετά τα πλαίσια του κάτω μέρους, ώστε να παίρνει τον χώρο που μένει)
        shape_frame = tk.Frame(root)
        tool_frame = tk.Frame(shape_frame)
        tool_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        self.tool_buttons = {}
        # R = reset offsets, C = calibrate (το σχήμα γίνεται 0,0,0)
        tool_commands = {"M": None, "R": self.reset_offsets, "C": self.calibrate}
        for text, command in tool_commands.items():
            button = tk.Button(tool_frame, text=text, width=2, padx=0, pady=0, command=command)
            button.pack(side=tk.TOP, pady=1)
            self.tool_buttons[text] = button
        self.canvas = tk.Canvas(shape_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg=CANVAS_BG_COLOR, highlightthickness=0)

        self.angle_titles = {"roll": "Roll (X)", "pitch": "Pitch (Z)", "yaw": "Yaw (Y)"}

        # 9. Πλαίσιο με sliders: τιμές προσανατολισμού χωρίς Sense HAT, αλλιώς offsets
        # (pack πρώτο με side=BOTTOM ώστε να βρίσκεται κάτω από το info_frame)
        control_frame = tk.Frame(root, relief=tk.SUNKEN, borderwidth=2)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        control_frame.columnconfigure(1, weight=1)
        title = "Orientation values" if self.sense is None else "Orientation offsets"
        tk.Label(control_frame, text=title, font="TkDefaultFont 9 bold").grid(
            row=0, column=0, columnspan=3, sticky=tk.W, padx=2)
        self.scale_vars = {}
        for row, (name, angle_title) in enumerate(self.angle_titles.items(), start=1):
            # Βήμα 0.1° ώστε το calibrate να φτάνει το σχήμα πρακτικά ακριβώς στο 0
            var = tk.DoubleVar(value=0.0)
            value_label = tk.Label(control_frame, text="0.0°", width=7, anchor=tk.E)
            tk.Label(control_frame, text=angle_title, anchor=tk.W).grid(row=row, column=0, sticky=tk.W, padx=2)
            tk.Scale(control_frame, variable=var, from_=-180, to=180, resolution=0.1, orient=tk.HORIZONTAL,
                     showvalue=False, width=10, sliderlength=15, borderwidth=1
                     ).grid(row=row, column=1, sticky=tk.EW, padx=2)
            var.trace_add("write", lambda *_, v=var, lbl=value_label: lbl.config(text=f"{round(v.get(), 1) + 0.0:.1f}°"))
            value_label.grid(row=row, column=2, padx=2)
            self.scale_vars[name] = var

        # 8. Πλαίσιο με τις τρέχουσες τιμές Roll / Pitch / Yaw κάτω από τον canvas
        # (pack πριν τον canvas, ώστε να μένει ορατό όταν μικραίνει το παράθυρο)
        info_frame = tk.Frame(root, relief=tk.SUNKEN, borderwidth=2)
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=(0, 2))
        self.angle_vars = {}
        for name, title in self.angle_titles.items():
            var = tk.StringVar(value=f"{title}: ---")
            tk.Label(info_frame, textvariable=var, width=12, anchor=tk.W,
                     font="TkDefaultFont").pack(side=tk.LEFT, expand=True, padx=2, pady=1)
            self.angle_vars[name] = var

        shape_frame.pack(padx=2, pady=2, fill=tk.BOTH, expand=True)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.view_size = (CANVAS_WIDTH, CANVAS_HEIGHT)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        # Η σκηνή σχεδιάζεται σε offscreen framebuffer με το μέγεθος του canvas,
        # ανεξάρτητα από το (κρυφό/ελαχιστοποιημένο) παράθυρο του pi3d
        self.offscreen = None
        self.offscreen_size = None

        self.canvas_image_id = self.canvas.create_image(0, 0, anchor=tk.NW)
        self.tk_image = None

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.render_loop()

    def _hide_pi3d_window(self):
        # Κρύβει το παράθυρο του pi3d: η εικόνα φτάνει στο Tk μέσω screenshot
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

    @staticmethod
    def _wrap_angle(angle):
        # Γωνία στο διάστημα -180..180 (ίδιο με το εύρος των sliders)
        return (angle + 180.0) % 360.0 - 180.0

    def calibrate(self):
        # Offsets = -(τιμές αισθητήρα), ώστε Roll, Pitch, Yaw του σχήματος = 0, 0, 0
        if self.sense is None:
            self.reset_offsets()
            return
        if self.sensor is None:
            self.sensor = self.sense.get_orientation()
        for name, var in self.scale_vars.items():
            var.set(self._wrap_angle(-self.sensor[name]))

    def reset_offsets(self):
        # Offsets = 0: το σχήμα ακολουθεί ξανά ακριβώς τον αισθητήρα
        for var in self.scale_vars.values():
            var.set(0.0)

    def _on_canvas_resize(self, event):
        self.view_size = (max(event.width, 1), max(event.height, 1))

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

    def close(self):
        self.pi3d_display.destroy()
        self.root.destroy()

    def render_loop(self):
        if self.view_size != self.offscreen_size:
            self._resize_view(*self.view_size)
        if self.pi3d_display.loop_running():
            # Χωρίς Sense HAT οι sliders δίνουν τις τιμές, αλλιώς προστίθενται ως offset
            orientation = {name: var.get() for name, var in self.scale_vars.items()}
            if self.sense is not None:
                self.sensor = self.sense.get_orientation()
                orientation = {name: self._wrap_angle(self.sensor[name] + offset)
                               for name, offset in orientation.items()}
            
            self.roll_node.rotateToX(orientation['roll'])
            self.pitch_node.rotateToZ(orientation['pitch'])
            self.yaw_node.rotateToY(orientation['yaw'])
            for name, var in self.angle_vars.items():
                var.set(f"{self.angle_titles[name]}: {round(orientation[name], 1) + 0.0:4.1f}°")

            self.offscreen.begin()
            self.yaw_node.draw(self.shader, camera=self.camera)
            grid_screenshot = self.offscreen.read_pixels()
            self.offscreen.end()
            pil_img = Image.fromarray(grid_screenshot)
            self.tk_image = ImageTk.PhotoImage(pil_img)
            self.canvas.itemconfig(self.canvas_image_id, image=self.tk_image)
            
            self.root.after(15, self.render_loop)
        else:
            self.close()

if __name__ == "__main__":
    window = tk.Tk()
    app = Transparent3DCubeApp(window)
    window.mainloop()

