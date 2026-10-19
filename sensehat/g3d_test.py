import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")  # Force Matplotlib to bind directly to Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class Matplotlib3DApp:
    def __init__(self, root):
        self.root = root
        self.root.title("General-Use 3D Tkinter Canvas")
        
        # 1. Create Matplotlib Figure and a 3D Projection space
        self.fig = Figure(figsize=(6, 5), dpi=100, facecolor='#111111')
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('#111111')
        
        # 2. Embed the Matplotlib backend widget directly into the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # 3. Build and plot the 3D scene elements
        self.setup_scene()
        
        # Enable default interactive mouse dragging to rotate the 3D space
        self.ax.mouse_init()

    def setup_scene(self):
        # Establish manual limit spans for the X, Y, and Z axis arrays from center
        self.ax.set_xlim([-2, 2])
        self.ax.set_ylim([-2, 2])
        self.ax.set_zlim([-2, 2])
        
        # Style and assign specific text labels to the active axis dimensions
        self.ax.set_xlabel('X Axis', color='#ff5555', fontweight='bold', fontsize=11)
        self.ax.set_ylabel('Y Axis', color='#55ff55', fontweight='bold', fontsize=11)
        self.ax.set_zlabel('Z Axis', color='#5555ff', fontweight='bold', fontsize=11)
        
        # Remove background panes for a transparent wireframe style
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        
        # Color matching axis ticks and numeric parameters
        self.ax.xaxis.label.set_color('#ff5555')
        self.ax.yaxis.label.set_color('#55ff55')
        self.ax.zaxis.label.set_color('#5555ff')
        self.ax.tick_params(colors='white')
        
        # Define Parallelogram 3D coordinates (Bottom Left, Bottom Right, Top Right, Top Left)
        vertices = np.array([
            [-1.2, -0.4, 0.2],
            [ 0.6, -0.4, 0.2],
            [ 1.2,  0.4, 0.2],
            [-0.6,  0.4, 0.2]
        ])
        
        # Add a filled solid 3D polygon plane to the axes object collection
        poly = Poly3DCollection([vertices], alpha=0.5, facecolor='cyan', edgecolor='white', linewidths=2)
        self.ax.add_collection3d(poly)
        
        # Anchor a persistent center text tracker label onto the 3D origin point (0,0,0)
        self.ax.text(0, 0, 0, "  Origin", color='white', weight='bold')

if __name__ == "__main__":
    root = tk.Tk()
    app = Matplotlib3DApp(root)
    root.mainloop()
