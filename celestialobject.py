import math
from tkinter import Canvas, messagebox


# Canvas Dimensions
WIDTH, HEIGHT = 900, 675
# Astronomical Units ( converted to meters )
AU = 149.6e6 * 1000
# Gravitational Constant
G = 6.67428e-11
# Scale factor
SCALE = 250 / AU # 1 AU = 250 pixels
# 1 day time step
TIMESTEP = 3600*24

class Vector2:
    def __init__(self, x, y) -> None:
        self.x, self.y = x, y

    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y

    def __ne__(self,other) -> bool:
        return not self.__eq__(other)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
            return self
        if isinstance(other, (int, float)):
            self.x += other
            self.y += other
            return self

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x * other.x, self.y * other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x / other.x, self.y / other.y)
        if isinstance(other, (int, float)):
            return Vector2(self.x / other, self.y / other)

    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def distance_to(self, other):
        return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)



class CelestialObject:
    def __init__(self, 
                origin: Vector2, 
                canvas: Canvas, 
                radius: int,
                mass: int,
                velocity: Vector2, 
                tag: str,
                ) -> None:

        self.real_position = Vector2(origin.x, origin.y)
        self.center = Vector2(0, 0)
        self.canvas = canvas
        self.radius = radius
        self.mass = mass
        self.velocity = velocity
        self.orbit = [self.center]
        self.sun = False
        self.distance_to_sun = 0
        self.color = "white"
        self.tag = tag

        self.update_screen_position()

    def update_screen_position(self):

        # Scale center position relative to canvas center
        self.center.x = self.real_position.x * SCALE + WIDTH / 2
        self.center.y = self.real_position.y * SCALE + HEIGHT / 2

    def __repr__(self) -> str:
        return f"{self.tag}"

    def draw(self, center):
        self.canvas.delete(self.tag)
        x1 = self.center.x - self.radius
        y1 = self.center.y - self.radius
        x2 = self.center.x + self.radius
        y2 = self.center.y + self.radius
        self.canvas.create_oval(x1, y1, x2, y2, fill="black", outline=self.color, tags=(self.tag))

    def attraction(self, other):

        # calculate distance between 2 objects
        distance_x = other.real_position.x - self.real_position.x
        distance_y = other.real_position.y - self.real_position.y
        distance = self.real_position.distance_to(other.real_position)

        # if other is sun, calculate distance to sun
        if( other.sun ):
            self.distance_to_sun = distance

        # Attraction force operations
        force = G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force

        return force_x, force_y


    # Sum force of attraction between current object and all other celestial objects
    def update_position(self, planets):

        total_force_x = total_force_y = 0

        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_force_x += fx
            total_force_y += fy

        self.velocity += Vector2(total_force_x, total_force_y) / self.mass * TIMESTEP

        self.real_position += self.velocity * TIMESTEP

        self.update_screen_position()

        self.orbit.append(self.center)

class ObjectManager:
    def __init__(self, canvas: Canvas, config: list) -> None:
        self.canvas = canvas
        self.celestialObjects = []
        self.config = config

        self.canvas.bind("<Button-1>", self.spawn_objectClick)

    # Spawn Celestial Object ( a Circle ) from click on canvas
    def spawn_objectClick(self, event):
        
        # Grab config info from config entries
        mass = self.config[0].get()             # This returns a string btw
        initial_velocity = self.config[1].get()
        tag = self.config[2].get()
        
        if(mass == ""):
            messagebox.showerror("Error", "Object must have mass.") 
            return
        if(initial_velocity == ""):
            messagebox.showerror("Error", "Object must have initial velocity")
            return
        if(tag == ""):
            messagebox.showerror("Error","Object must have a tag (Name)")
            return


        real_x = (event.x - WIDTH/2) / SCALE
        real_y = (event.y - HEIGHT/2) / SCALE

        new_object = CelestialObject(
            Vector2(real_x, real_y), 
            self.canvas,
            10,
            float(mass),
            Vector2(0, float(initial_velocity)),
            tag
        )
        self.celestialObjects.append(new_object)
    
    # Spawn Celestial Object ( a Circle ) with hardcoded values
    def spawn_object_hard(self, center, radius, mass, initial_v, tag):

        new_object = CelestialObject(
            center,
            self.canvas,
            radius,
            mass,
            initial_v,
            tag
        )
        
        self.celestialObjects.append(new_object)


    def spawn_sun(self):
        
        # mass of the sun
        mass = 1.98892 * 10**30

        new_object = CelestialObject(
            Vector2(0, 0),
            self.canvas,
            20,
            mass,
            Vector2(0,0),
            "Sun"
        )
        new_object.sun = True
        new_object.distance_to_sun = 0

        self.celestialObjects.append(new_object)

    def update_objects(self):

        for planet in self.celestialObjects:
            planet.draw(planet.center)
            planet.update_position(self.celestialObjects)
        self.canvas.after(100, self.update_objects)
