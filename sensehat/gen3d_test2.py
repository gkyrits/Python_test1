import tkinter as tk
from OpenGL import GL, GLU
from pyopengltk import OpenGLFrame

class RotatingCubeFrame(OpenGLFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.angle = 0.0  # Initial rotation angle
        
        # Bind mouse dragging to change rotation speed or angle manually
        self.bind("<B1-Motion>", self.mouse_drag)
        self.last_x = 0
        self.last_y = 0
        self.bind("<Button-1>", self.save_mouse_pos)

    def initgl(self):
        """Called once when the OpenGL context is created."""
        # Enable depth testing so faces render in the correct 3D order
        GL.glEnable(GL.GL_DEPTH_TEST)
        
        # Set background clear color to dark gray
        GL.glClearColor(0.15, 0.15, 0.15, 1.0)
        
        # Setup perspective projection matrix
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, self.width / self.height, 0.1, 50.0)
        
        # Switch back to modelview matrix for drawing shapes
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def redraw(self):
        """Called automatically every frame to redraw the 3D scene."""
        # Clear color and depth buffers
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        
        # Move the camera back slightly so we can see the cube
        GL.glTranslatef(0.0, 0.0, -6.0)
        
        # Rotate the scene around the X, Y, and Z axes
        GL.glRotatef(self.angle, 1.0, 1.0, 1.0)
        
        self.draw_cube()
        
        # Increment rotation angle for the next frame animation
        self.angle += 1.0

    def draw_cube(self):
        """Defines the 8 corners and 6 colored faces of a cube."""
        # Define the 8 vertices of the cube
        vertices = [
            [-1.0, -1.0,  1.0], [ 1.0, -1.0,  1.0], [ 1.0,  1.0,  1.0], [-1.0,  1.0,  1.0],
            [-1.0, -1.0, -1.0], [ 1.0, -1.0, -1.0], [ 1.0,  1.0, -1.0], [-1.0,  1.0, -1.0]
        ]
        
        # Define the 6 faces using indices of the vertices array
        faces = [
            (0, 1, 2, 3), # Front (Cyan)
            (1, 5, 6, 2), # Right (Orange)
            (5, 4, 7, 6), # Back (Green)
            (4, 0, 3, 7), # Left (Red)
            (3, 2, 6, 7), # Top (Blue)
            (4, 5, 1, 0)  # Bottom (Magenta)
        ]
        
        # RGB colors for each face
        colors = [
            (0, 1, 1), (1, 0.5, 0), (0, 1, 0), 
            (1, 0, 0), (0, 0, 1), (1, 0, 1)
        ]
        
        # Begin rendering quads (4-sided polygons)
        GL.glBegin(GL.GL_QUADS)
        for i, face in enumerate(faces):
            GL.glColor3fv(colors[i])
            for vertex in face:
                GL.glVertex3fv(vertices[vertex])
        GL.glEnd()

    # Optional Interactivity
    def save_mouse_pos(self, event):
        self.last_x = event.x
        self.last_y = event.y

    def mouse_drag(self, event):
        """Speeds up or shifts rotation based on manual dragging."""
        dx = event.x - self.last_x
        self.angle += dx * 0.5
        self.save_mouse_pos(event)

# --- Standard Tkinter Application Setup ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("pyopengltk Native 3D Canvas Example")
    root.geometry("600x650")

    # App Title Label
    label = tk.Label(root, text="OpenGL 3D Engine inside Tkinter", font=("Arial", 14, "bold"))
    label.pack(pady=10)

    # Instantiate the custom OpenGL Widget Frame
    app_3d = RotatingCubeFrame(root, width=500, height=500)
    app_3d.pack(fill=tk.BOTH, expand=tk.YES, padx=20, pady=10)
    
    # 1 tells pyopengltk to loop via Tkinter's millisecond clock for smooth animation
    app_3d.animate = 1 

    # Example of standard Tkinter layouts co-existing seamlessly
    btn_quit = tk.Button(root, text="Quit Application", command=root.quit, bg="#d9534f", fg="white", padx=10)
    btn_quit.pack(side=tk.BOTTOM, pady=15)

    root.mainloop()
