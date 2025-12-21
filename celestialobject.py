import math
from tkinter import Canvas, messagebox

# Astronomical Units ( converted to meters )
AU = 149.6e6 * 1000
# Gravitational Constant
G = 6.67428e-11
# Scale factor
SCALE = 250 / AU # 1 AU = 100 pixels

class Vector2:
    def __init__(self, x, y) -> None:
        self.x, self.y = x, y



class CelestialObject:
    def __init__(self, 
                origin: Vector2, 
                canvas: Canvas, 
                radius: int,
                mass: int, 
                tag: str,
                ) -> None:
        self.center = Vector2(origin.x, origin.y)
        self.canvas = canvas
        self.radius = radius
        self.mass = mass
        self.velocity = Vector2(0,0)
        self.sun = False
        self.distance_to_sun = 0
        self.color = "white"
        self.tag = tag

    def draw(self):
        x1 = self.center.x - self.radius
        y1 = self.center.y - self.radius
        x2 = self.center.x + self.radius
        y2 = self.center.y + self.radius
        self.canvas.create_oval(x1, y1, x2, y2, fill="black", outline=self.color)



class ObjectManager:
    def __init__(self, canvas: Canvas, config: list) -> None:
        self.canvas = canvas
        self.celestialObjects = []
        self.config = config

        self.canvas.bind("<Button-1>", self.spawn_object)

    # Spawn Celestial Object ( a Circle )
    def spawn_object(self, event):
        
        # Grab config info from config entries
        mass = self.config[0].get()
        
        if(mass == ""):
            messagebox.showerror("Error", "Object must have mass.") 
            return

        new_object = CelestialObject(
            Vector2(event.x, event.y), 
            self.canvas,
            10,
            mass,
            "object"
        )
        self.celestialObjects.append(new_object)
        new_object.draw()

    def spawn_sun(self, width, height):

        mass = 1000

        x = width // 2
        y = height // 2

        new_object = CelestialObject(
            Vector2(x, y),
            self.canvas,
            15,
            mass,
            "Sun"
        )
        new_object.sun = True
        new_object.distance_to_sun = 0

        self.celestialObjects.append(new_object)
        new_object.draw()