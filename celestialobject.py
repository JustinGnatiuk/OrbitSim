import math
import tkinter as tk
from tkinter import Tk, Canvas, messagebox


# Canvas Dimensions
WIDTH, HEIGHT = 900, 675

# Convert mass and velocity entry expressions to float values
def expression_convert(expression):

    if expression is None:
        return None

    expression = str(expression).strip().replace(' ', '')

    # If expression is already a simple float
    try:
        return float(expression)
    except ValueError:
        pass

    # Replace exponent notations and multiplication characters
    expression = expression.replace('x10^', '*10**')
    expression = expression.replace('x10**', '*10**')
    expression = expression.replace('^', '**')
    expression = expression.replace('x', '*')

    # Character security check
    allowed_chars = set("-0123456789.*")
    if not all(c in allowed_chars for c in expression.replace('**', '')):
        print(expression)
        raise ValueError("Invalid Expression, forbidden characters present")

    # evaluate sanitized expression
    try:
        return float(eval(expression, {"__builtins__": {}}, {}))
    except:
        raise ValueError("Invalid Expression")
     

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
    def __init__(
                self, 
                origin: Vector2, 
                canvas: Canvas, 
                radius: int,
                mass: int,
                velocity: Vector2, 
                tag: str,
                object_manager
                ) -> None:

        self.real_position = Vector2(origin.x, origin.y)
        self.center = Vector2(0, 0)
        self.canvas = canvas
        self.base_radius = radius
        self.radius = radius
        self.mass = mass
        self.velocity = velocity
        self.orbit = []
        self.orbit_line_id = None
        self.oval_id = None
        self.sun = False
        self.distance_to_sun = 0
        self.color = "white"
        self.tag = tag
        self.object_manager = object_manager
        self.orbital_length = 100000

        self.update_radius()
        self.update_screen_position()

        self.canvas.tag_bind(self.tag, "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.tag, "<Button-1>", self.on_click)
        self.canvas.tag_bind(self.tag, "<Button-3>", self.delete_planet_onClick)

    def update_screen_position(self):

        # Scale center position relative to canvas center
        self.center.x = self.real_position.x * self.object_manager.settings.SCALE + WIDTH / 2
        self.center.y = self.real_position.y * self.object_manager.settings.SCALE + HEIGHT / 2

    def __repr__(self) -> str:
        return f"{self.tag}"

    def on_enter(self, event):
        return

    def on_click(self, event):
        self.object_manager.update_callback(self)

    def draw(self):

        if self.oval_id is None:

            x1 = self.center.x - self.radius
            y1 = self.center.y - self.radius
            x2 = self.center.x + self.radius
            y2 = self.center.y + self.radius
            if( self.sun ):
                self.oval_id = self.canvas.create_oval(x1, y1, x2, y2, fill="yellow", outline=self.color, tags=(self.tag))
            else:
                self.oval_id = self.canvas.create_oval(x1, y1, x2, y2, fill="black", outline=self.color, tags=(self.tag))

        else:
            x1 = self.center.x - self.radius
            y1 = self.center.y - self.radius
            x2 = self.center.x + self.radius
            y2 = self.center.y + self.radius
            self.canvas.coords(self.oval_id, x1, y1, x2, y2)

    def attraction(self, other):

        # calculate distance between 2 objects
        distance_x = other.real_position.x - self.real_position.x
        distance_y = other.real_position.y - self.real_position.y
        distance = self.real_position.distance_to(other.real_position)

        # if other is sun, calculate distance to sun
        if( other.sun ):
            self.distance_to_sun = distance

        # Attraction force operations
        force = self.object_manager.settings.G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force

        return force_x, force_y


    # Sum force of attraction between current object and all other celestial objects
    def update_position(self, planets):
        
        # Total force by all other planets
        total_force_x = total_force_y = 0

        # Add up total force by all other planets
        for planet in planets:
            if self == planet:
                continue
            fx, fy = self.attraction(planet)
            total_force_x += fx
            total_force_y += fy

        # Calculate velocity from forces in x,y directions
        self.velocity += Vector2(total_force_x, total_force_y) / self.mass * self.object_manager.settings.TIMESTEP

        # Increment position based on velocity and time
        self.real_position += self.velocity * self.object_manager.settings.TIMESTEP


        # Calculate position on screen based on real position
        self.update_screen_position()

        # Add point for orbit visualization
        self.orbit.append(Vector2(self.center.x, self.center.y))

    def draw_orbit(self):

        coords = [coord for v in self.orbit for coord in (v.x, v.y)]

        if not coords or len(coords) < 4:
            return

        if self.orbit_line_id is None:
            self.orbit_line_id = self.canvas.create_line(
                *coords,
                dash=(5,2),
                smooth=True,
                fill="white",
                width=1,
                splinesteps=5,
                tags=f"{self.tag}_orbit"
            )
        else:
            # Update existing orbit line
            self.canvas.coords(self.orbit_line_id, *coords)

        # Limit orbit points to prevent overlap
        current_x = round(self.orbit[-1].x, 2)
        initial_x = round(self.orbit[0].x, 2)
        current_y = round(self.orbit[-1].y, 2)
        initial_y = round(self.orbit[0].y, 2)
        
        # Check difference between current orbit coordinates and initial
        if(len(self.orbit) > 50):
            if( round(abs(current_x - initial_x) , 2) < 3 and round(abs(current_y - initial_y) , 2) < 3):
                self.orbital_length = len(self.orbit)
            self.orbit = self.orbit[-self.orbital_length:]
            


    def update_radius(self):
        self.radius = self.object_manager.settings.zoom * self.base_radius

    def delete_planet_onClick(self, event):
        
        # Do not remove sun
        if( self.sun ):
            messagebox.showerror("Error", "Cannot remove sun")
            return

        # Remove visual elements on canvas
        if( self.oval_id ):
            self.canvas.delete(self.oval_id)
        if( self.orbit_line_id ):
            self.canvas.delete(self.oval_id)

        # Delete tag references to planet
        self.canvas.delete(f"{self.tag}")
        self.canvas.delete(f"{self.tag}_orbit")

        # Remove event bindings
        self.canvas.tag_unbind(self.tag, "<Enter>")
        self.canvas.tag_unbind(self.tag, "<Button-1>")
        self.canvas.tag_unbind(self.tag, "<Button-3>")

        # Remove planet from object manager celestial objects list
        for i, planet in enumerate(self.object_manager.celestialObjects):
            if planet.tag == self.tag:
                self.object_manager.celestialObjects.pop(i)
                break

        self.oval_id = None
        self.orbit_line_id = None
        self.orbit = []

        if( hasattr(self.object_manager, 'selected_planet') and self.object_manager.selected_planet ):
            if( self.object_manager.selected_planet.tag == self.tag ):
                self.object_manager.clear_callback()

class ObjectManager:
    def __init__(
                self, 
                canvas: Canvas, 
                config: dict, 
                settings, 
                update_callback=None,
                clear_callback=None
                ) -> None:
        self.canvas = canvas
        self.celestialObjects = []
        self.config = config
        self.settings = settings
        self.update_callback = update_callback
        self.clear_callback = clear_callback
        self.selected_planet = None
        self.empty_solar_system = self.canvas.create_text(
                10, 665,                     
                text="The universe is a vast, cold, and empty place...",  
                font=("Verdana", 8, "bold italic"),  
                fill="white",              
                anchor="w",            
                width=500,
                tags="no_planets",
                state="normal"                                
            )

        self.canvas.bind("<Button-1>", self.spawn_objectClick)

    # Spawn Celestial Object ( a Circle ) from click on canvas
    def spawn_objectClick(self, event):

        # Check if an item on the canvas was clicked or the background itself
        clicked_items = event.widget.find_withtag(tk.CURRENT)
        
        if clicked_items:
            return
        else:
            # Grab config info from config entries
            mass = self.config['mass'].get()                              # This returns a string btw
            initial_velocity_x = self.config['initial_velocity_x'].get()  # This returns a string btw
            initial_velocity_y = self.config['initial_velocity_y'].get()  # This returns a string btw
            radius = self.config['radius'].get()                          # This returns a string btw
            tag = self.config['tag'].get()

            if(mass == ""):
                messagebox.showerror("Error", "Object must have mass.") 
                return
            if(initial_velocity_x == ""):
                messagebox.showerror("Error", "Object must have initial velocity in x direction")
                return
            if(initial_velocity_y == ""):
                messagebox.showerror("Error", "Object must have initial velocity in y direction")
                return
            if(radius == ""):
                messagebox.showerror("Error", "Object must have radius, I suggest between 5 and 20")
            if(tag == ""):
                messagebox.showerror("Error","Object must have a tag (Name)")
                return

            # Convert mass and velocity expressions
            try:
                mass = expression_convert(mass)
            except ValueError as e:
                messagebox.showerror("Error", f"{e} (mass)")
                return

            try:
                initial_velocity_x = expression_convert(initial_velocity_x)
            except ValueError as e:
                messagebox.showerror("Error", f"{e} (initial velocity x)")
                return

            try:
                initial_velocity_y = expression_convert(initial_velocity_y)
            except ValueError as e:
                messagebox.showerror("Error", f"{e} (initial velocity y)")
                return

            # Calculate real coordinate distance
            real_x = (event.x - WIDTH/2) / self.settings.SCALE
            real_y = (event.y - HEIGHT/2) / self.settings.SCALE

            # Create new celestial object
            new_object = CelestialObject(
                Vector2(real_x, real_y), 
                self.canvas,
                float(radius),
                mass,
                Vector2(initial_velocity_x, initial_velocity_y),
                tag,
                self
            )
            self.celestialObjects.append(new_object)

            new_object.draw()

            self.config['mass'].delete(0, tk.END)
            self.config['initial_velocity_x'].delete(0, tk.END)
            self.config['initial_velocity_y'].delete(0, tk.END)
            self.config['radius'].delete(0, tk.END)
            self.config['tag'].delete(0, tk.END)
    
    # Spawn Celestial Object ( a Circle ) with hardcoded values
    def spawn_object_hard(self, center, radius, mass, initial_v, tag):

        new_object = CelestialObject(
            center,
            self.canvas,
            radius,
            mass,
            initial_v,
            tag,
            self
        )
        self.celestialObjects.append(new_object)


    def spawn_sun(self):
        
        # mass of the sun
        mass = 1.98892 * 10**30

        new_object = CelestialObject(
            Vector2(0, 0),
            self.canvas,
            10,
            mass,
            Vector2(0,0),
            "Sun",
            self
        )
        new_object.sun = True
        new_object.distance_to_sun = 0

        self.celestialObjects.append(new_object)

    def reset_sun_position(self):

        for planet in self.celestialObjects:

            if( planet.sun ):

                planet.real_position = Vector2(0,0)
                planet.velocity = Vector2(0,0)

    def clear_planets(self):

        result = messagebox.askyesno("Warning", "Are you sure you want to remove all planets?")

        if( result ):

            # Make copy to avoid modification when iterating
            planets_list = self.celestialObjects.copy()

            for planet in planets_list:

                # skip sun
                if( not planet.sun ):
                    # delete canvas visual elements
                    if( planet.oval_id ):
                        self.canvas.delete(planet.oval_id)
                    if( planet.orbit_line_id ):
                        self.canvas.delete(planet.orbit_line_id)

                    # delete canvas tags
                    self.canvas.delete(planet.tag)
                    self.canvas.delete(f"{planet.tag}_orbit")

                    # remove event bindings
                    self.canvas.tag_unbind(planet.tag, "<Enter>")
                    self.canvas.tag_unbind(planet.tag, "<Button-1>")
                    self.canvas.tag_unbind(planet.tag, "<Button-3>")

                    # remove from celestialObjects list
                    if( planet in self.celestialObjects ):
                        self.celestialObjects.remove(planet)
                else:
                    self.reset_sun_position()

            # Clear selected planet from info frame
            self.selected_planet = None
            if( self.clear_callback ):
                self.clear_callback()
        
        else:
            return

    def update_objects(self):

        if( len(self.celestialObjects) == 1):

            self.canvas.itemconfig(self.empty_solar_system, state="normal")

        else:
            
            self.canvas.itemconfig(self.empty_solar_system, state="hidden")

            if( not self.config['pause'] ):
                orbit_option = self.config['draw_orbit'].get()

                for planet in self.celestialObjects:

                    planet.draw()
                    planet.update_position(self.celestialObjects)
                    # Draw orbits
                    if(planet.tag != "Sun" and orbit_option):
                        planet.draw_orbit()
                    # if orbit option deselected, remove orbit lines
                    if( not orbit_option and planet.orbit_line_id ):
                        self.canvas.delete(f"{planet.tag}_orbit")
                        planet.orbit_line_id = None

            if( hasattr(self, 'selected_planet') and self.selected_planet ):
                self.update_callback(self.selected_planet)

        
        self.canvas.after(self.settings.SPEED, self.update_objects)
