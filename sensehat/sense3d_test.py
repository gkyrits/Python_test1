import pi3d
import tkinter as tk
from PIL import Image, ImageTk

try:
    from sense_hat import SenseHat
except ImportError:
    try:
        from sense_emu import SenseHat
    except ImportError:
        SenseHat = None

class Transparent3DCubeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Independent Cuboid Dimensions")
        
        if SenseHat is not None:
            self.sense = SenseHat()
            self.sense.clear()
        else:
            self.sense = None
        
        # 1. ΟΡΙΣΤΕ ΕΔΩ ΤΙΣ ΑΝΕΞΑΡΤΗΤΕΣ ΔΙΑΣΤΑΣΕΙΣ (Width, Height, Depth)
        MY_W = 1.6  # Μήκος (Άξονας X)
        MY_H = 0.2  # Ύψος (Άξονας Y)
        MY_D = 1.0  # Βάθος (Άξονας Z)
        
        # Υπολογισμός των μισών αποστάσεων από το κέντρο (extents)
        xw, yh, zd = MY_W / 2.0, MY_H / 2.0, MY_D / 2.0
        
        # 2. Αρχικοποίηση pi3D Display
        self.pi3d_display = pi3d.Display.create(w=500, h=500, background=(0.1, 0.1, 0.1, 1.0))
        self.pi3d_display.resize(x=0, y=self.pi3d_display.max_height, w=500, h=500)
        
        self.shader = pi3d.Shader("mat_flat")
        
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
        self.canvas = tk.Canvas(root, width=500, height=500, bg="black")
        self.canvas.pack(padx=10, pady=10)
        
        self.canvas_image_id = self.canvas.create_image(0, 0, anchor=tk.NW)
        self.tk_image = None

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.render_loop()

    @staticmethod
    def _empty_node(z=0.0):
        # Γραμμή μηδενικού μήκους: δεν φαίνεται, χρησιμεύει μόνο ως γονέας
        return pi3d.Lines(vertices=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], z=z)

    def close(self):
        self.pi3d_display.destroy()
        self.root.destroy()

    def render_loop(self):
        if self.pi3d_display.loop_running():
            if self.sense is None:
                orientation = {'pitch': 0, 'yaw': 0, 'roll': 0}
            else:
                orientation = self.sense.get_orientation()
            
            self.roll_node.rotateToX(orientation['roll'])
            self.pitch_node.rotateToZ(orientation['pitch'])
            self.yaw_node.rotateToY(orientation['yaw'])

            self.yaw_node.draw(self.shader)
            
            grid_screenshot = pi3d.screenshot()
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

