import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # Force Matplotlib to use the Tkinter backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class Rotating3DApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Rotating Cuboid with Different Dimensions")
        
        # 1. Setup Matplotlib Figure and a clean dark 3D Subplot
        self.fig = Figure(figsize=(6, 6), dpi=100, facecolor='#111111')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#111111')
        
        # Hide default background panels and grid lines
        self.ax.grid(False)
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        self.ax.axis('off')  # Turn off standard bounding boxes
        
        # Set spatial scale limits around the center (0,0,0)
        self.ax.set_xlim([-2.5, 2.5])
        self.ax.set_ylim([-2.5, 2.5])
        self.ax.set_zlim([-2.5, 2.5])
        
        # 2. Embed into Tkinter layout
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # 3. Create Fixed 3D Axes Elements
        self.setup_static_elements()
        
        # 4. Define custom X, Y, Z total length dimensions (half-extents from center)
        # Edit these to change the box size!
        dim_x = 2.6  # Width
        dim_y = 1.8  # Depth
        dim_z = 1.4  # Height
        
        # Define 8 vertices of the cuboid
        dx, dy, dz = dim_x / 2.0, dim_y / 2.0, dim_z / 2.0
        vertices = np.array([
            [-dx, -dy, -dz],  # 0
            [ dx, -dy, -dz],  # 1
            [ dx,  dy, -dz],  # 2
            [-dx,  dy, -dz],  # 3
            [-dx, -dy,  dz],  # 4
            [ dx, -dy,  dz],  # 5
            [ dx,  dy,  dz],  # 6
            [-dx,  dy,  dz]   # 7
        ])
        
        # Group the vertices into 6 distinct rectangular faces
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # Bottom
            [vertices[4], vertices[5], vertices[6], vertices[7]],  # Top
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # Front
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # Back
            [vertices[0], vertices[3], vertices[7], vertices[4]],  # Left
            [vertices[1], vertices[2], vertices[6], vertices[5]]   # Right
        ]
        
        # Add the 3D solid cuboid faces into the collection plot context
        self.box_collection = Poly3DCollection(faces, alpha=0.4, 
                                               facecolor='#00cccc', edgecolor='white', linewidths=1.5)
        self.ax.add_collection3d(self.box_collection)
        
        # 5. Start the Rotation Loop
        self.angle = 0
        self.animate()

    def setup_static_elements(self):
        """Draws the X, Y, Z vector arrows and anchoring text labels from the center."""
        length = 2.0
        
        # X Axis (Red)
        self.ax.quiver(0, 0, 0, length, 0, 0, color='#ff4444', arrow_length_ratio=0.12, linewidth=2)
        self.ax.text(length + 0.1, 0, 0, "X Axis", color='#ff4444', weight='bold', fontsize=10)
        
        # Y Axis (Green)
        self.ax.quiver(0, 0, 0, 0, length, 0, color='#44ff44', arrow_length_ratio=0.12, linewidth=2)
        self.ax.text(0, length + 0.1, 0, "Y Axis", color='#44ff44', weight='bold', fontsize=10)
        
        # Z Axis (Blue)
        self.ax.quiver(0, 0, 0, 0, 0, length, color='#4444ff', arrow_length_ratio=0.12, linewidth=2)
        self.ax.text(0, 0, length + 0.1, "Z Axis", color='#4444ff', weight='bold', fontsize=10)
        
        # Center Origin Label
        self.ax.text(0, 0, -0.15, "Origin (0,0,0)", color='white', ha='center', fontsize=9)

    def animate(self):
        """Looping animation modifying the viewing perspective angles automatically."""
        self.angle = (self.angle + 1) % 360
        
        # Set camera viewing angle (elev=vertical incline angle, azim=rotation)
        self.ax.view_init(elev=22, azim=self.angle)
        
        # Repaint changes to the canvas interface
        self.canvas.draw()
        
        # Call the next frame update (~30 FPS)
        self.root.after(30, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    app = Rotating3DApp(root)
    root.mainloop()
