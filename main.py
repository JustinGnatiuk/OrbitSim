import math
import tkinter as tk
from tkinter import Canvas, Tk, ttk, IntVar
from celestialobject import ObjectManager, Vector2


WIDTH, HEIGHT = 1200, 675

# TO DO 
class SimulationSettings():
    def __init__(self):
        # Astronomical Units ( converted to meters )
        self.AU = 149.6e6 * 1000
        # Gravitational Constant
        self.G = 6.67428e-11
        # Zoom Factor
        self.zoom = 1.0
        # pixels per AU
        self.base_pixels_per_au = 200
        # 1 day time step
        self.TIMESTEP = 3600*24
        # simulation speed in ms
        self.SPEED = 50

    @property
    def SCALE(self):
        return (self.base_pixels_per_au * self.zoom / self.AU) 

class OrbitSimulation:
    def __init__(self,root):
        self.root = root
        self.root.title("Orbit Simulation - github.com/JustinGnatiuk")
        self.root.resizable(0,0)
        self.canvas = None
        self.object_manager = None
        self.object_config = {
            'mass' : None,
            'initial_velocity' : None,
            'tag' : None,
            'draw_orbit' : None,
            'pause' : 0
        }
        self.simulation_settings = SimulationSettings()

        self.build_gui()

    def build_gui(self):

        # Create Main Container
        main_container = ttk.Frame(self.root, width=WIDTH, height=HEIGHT)
        main_container.pack(fill='both', expand=False)
        main_container.pack_propagate(False)

        # Create Simulation Canvas
        self.canvas = Canvas(main_container, width=WIDTH-300, height=HEIGHT, bg='black')
        self.canvas.pack(side='left', fill='both', expand=False)
        
        # Create Side Configuration Bar
        side_config = ttk.Frame(main_container, width=300)
        side_config.pack(side='right', fill='y', expand=False)
        side_config.pack_propagate(False)

        title_label = ttk.Label(
            side_config, 
            text="Python Orbit Simulator", 
            anchor='center',
            font=('Arial', 14, 'bold underline')
            )
        title_label.pack(side='top', fill='x', pady=(10,20))

        # Create form input container
        form_frame = ttk.Frame(side_config)
        form_frame.pack(fill='both', expand=True, anchor='nw', padx=0)

        # Object mass label and entry form
        mass_label = ttk.Label(form_frame, text='Mass (kg):', anchor='w', font=('Arial', 12))
        mass_label.grid(row=0, column=0, sticky='w', padx=(5,0), pady=5)
        mass_entry = ttk.Entry(form_frame, width=15)
        mass_entry.grid(row=0, column=1, sticky='w', padx=(5,0), pady=5)
        self.object_config['mass'] = mass_entry

        # Object initial velocity in x direction label and entry form
        initial_velocity_x = ttk.Label(form_frame, text="Velocity x (km/s): ", anchor='w', font=('Arial', 12))
        initial_velocity_x.grid(row=1, column=0, sticky='w', padx=(5,0), pady=5)
        initial_velocity_x_entry = ttk.Entry(form_frame, width=15)
        initial_velocity_x_entry.grid(row=1, column=1, sticky='w', padx=(5,0), pady=5)
        self.object_config['initial_velocity_x'] = initial_velocity_x_entry

        # Object initial velocity in y direction label and entry form
        initial_velocity_y = ttk.Label(form_frame, text="Velocity y (km/s): ", anchor='w', font=('Arial', 12))
        initial_velocity_y.grid(row=2, column=0, sticky='w', padx=(5,0), pady=5)
        initial_velocity_y_entry = ttk.Entry(form_frame, width=15)
        initial_velocity_y_entry.grid(row=2, column=1, sticky='w', padx=(5,0), pady=5)
        self.object_config['initial_velocity_y'] = initial_velocity_y_entry
        
        # Object tag label and entry form
        tag_label = ttk.Label(form_frame, text="Tag:", anchor='w', font=('Arial', 12))
        tag_label.grid(row=3, column=0, sticky='w', padx=(5,0), pady=5)
        tag_entry = ttk.Entry(form_frame, width=15)
        tag_entry.grid(row=3, column=1, sticky='w', padx=(5,0), pady=5)
        self.object_config['tag'] = tag_entry
        
        # Orbit Lines label and button
        orbit_var = IntVar()
        orbit_option = ttk.Checkbutton(form_frame, text="Draw Orbits ", variable=orbit_var)
        orbit_option.grid(row=4, column=0, sticky='w', padx=(5,0), pady=5)
        self.object_config['draw_orbit'] = orbit_var

        # Orbit pause/unpause button
        orbit_pause = ttk.Button(form_frame, text="Pause", command=lambda: self.toggle_pause(orbit_pause))
        orbit_pause.grid(row=4, column=1, sticky='w', padx=(5,0), pady=5)

        # Spawn planets button
        spawn_planets = ttk.Button(form_frame, text="Spawn Planets", command=self.spawn_planets)
        spawn_planets.grid(row=5, column=0, sticky='w', padx=(5,0), pady=5)

        # zoom scale slider
        zoom_scale = tk.Scale(
            form_frame,
            from_=0.1,
            to=2.5,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            label="Zoom Scale",
            length=200,
            command=self.update_zoom
        )
        zoom_scale.set(1.0) # default zoom
        zoom_scale.grid(row=6, column=0, sticky='w', padx=(5,0), pady=5, columnspan=2)

        # speed slider
        speed_scale = tk.Scale(
            form_frame,
            from_=10,
            to=100,
            resolution=10,
            orient=tk.HORIZONTAL,
            label="Speed ( ms )",
            length=200,
            command=self.update_speed
        )
        speed_scale.set(50) # default speed in ms
        speed_scale.grid(row=7, column=0, sticky='w', padx=(5,0), pady=5, columnspan=2)

        # Create a frame specifically for planet info in bottom right
        info_frame = ttk.LabelFrame(side_config, text="Planet Information", padding="10", width=100)
        info_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10, expand=True)

        # Create labels to display planet information
        # You can customize these based on what data you want to show
        self.info_labels = {}

        # Planet name/tag
        self.info_labels['tag'] = ttk.Label(info_frame, text="Tag: None", font=('Arial', 10, 'bold'))
        self.info_labels['tag'].pack(anchor=tk.W, pady=(0, 5))

        # Mass information
        self.info_labels['mass'] = ttk.Label(info_frame, text="Mass: 0.0")
        self.info_labels['mass'].pack(anchor=tk.W)

        # Velocity information
        self.info_labels['velocity'] = ttk.Label(info_frame, text="Velocity: (0.0, 0.0)")
        self.info_labels['velocity'].pack(anchor=tk.W)

        # Position information
        self.info_labels['position'] = ttk.Label(info_frame, text="Position: (0.0, 0.0)")
        self.info_labels['position'].pack(anchor=tk.W)

        # Distance from center/origin
        self.info_labels['distance'] = ttk.Label(info_frame, text="Distance from Sun: 0.0")
        self.info_labels['distance'].pack(anchor=tk.W, pady=(5, 0))

        # Clear planets button
        clear_planets = ttk.Button(form_frame, text="Clear Planets", command=self.clear_planets)
        clear_planets.grid(row=8, column=0, sticky='w', padx=(5,0), pady=5)

    def update_planet_info(self, planet):
        
        # set selected planet of objectManager class
        self.orbit_simulator.selected_planet = planet

        self.info_labels['tag'].config(text=f"Tag: {planet.tag}")

        self.info_labels['mass'].config(text=f"Mass: {planet.mass:.3e} kg")
        
        self.info_labels['velocity'].config(text=f"Velocity: ( {planet.velocity.x/1000:.1f} , {planet.velocity.y/1000:.1f} ) km/s")

        # format position for AU
        x_au = abs(planet.real_position.x / self.simulation_settings.AU)
        y_au = abs(planet.real_position.y / self.simulation_settings.AU)
        self.info_labels['position'].config(text=f"Position: ( {x_au:.3f} , {y_au:.3f} ) AU")

        # format distance to sun for AU
        au_distance = planet.distance_to_sun / self.simulation_settings.AU
        self.info_labels['distance'].config(text=f"Distance from sun: {au_distance:.3f} AU")

    def clear_planet_info(self):

        # clear selected planet of objectManager class
        self.orbit_simulator.selected_planet = None

        self.info_labels['tag'].config(text="Tag: None")
        self.info_labels['mass'].config(text="Mass: 0.0")
        self.info_labels['velocity'].config(text="Velocity: (0.0, 0.0)")
        self.info_labels['position'].config(text="Position: (0.0, 0.0)")
        self.info_labels['distance'].config(text="Distance from Sun: 0.0")

    def update_zoom(self, value):
        
        # update simulation settings zoom value
        self.simulation_settings.zoom = float(value)
        # remove all orbits for redraw
        for planet in self.orbit_simulator.celestialObjects:
            self.canvas.delete(f"{planet.tag}_orbit")
            planet.orbit_line_id = None
            planet.orbit = []
            planet.update_radius()
            planet.update_screen_position()
            planet.draw()

    def clear_planets(self):
        
        self.orbit_simulator.clear_planets()
            

    def update_speed(self, value):
        self.simulation_settings.SPEED = value

    def toggle_pause(self, pause_button):
        if( self.object_config['pause'] ):
            pause_button.config(text="Pause")
            self.object_config['pause'] = 0
            print("Continuing sim...")
        else:
            pause_button.config(text="Continue")
            self.object_config['pause'] = 1
            print("Pausing sim...")

    def add_planet(self, name, semi_major_axis_au, eccentricity, mass, radius, start_angle_deg=0, at_perihelion=True):
        
        """
        Add planet with realistic orbital parameters

        semi_major_axis_au: length of Semi-major axis in AU
        eccentricity: orbital eccentricity (0=circular)
        mass: mass in kg
        radius: visual radius of planet
        start_angle_deg: starting angular position (0 degrees = positive x axis)
        at_perihelion: true if starting at closest point to sun
        """

        sun_mass = 1.98892 * 10**30

        if at_perihelion:
            # Perihelion distance = a(1-e)
            distance = semi_major_axis_au * self.simulation_settings.AU * (1 - eccentricity)
            # speed at perihelion from vis-viva equation: v squared = GM(2/r - 1/a)
            a = semi_major_axis_au * self.simulation_settings.AU # Convert to meters
            speed = math.sqrt(self.simulation_settings.G * sun_mass * (2/distance - 1/a))
        else:
            # Aphelion distance = a(1+e)
            distance = semi_major_axis_au * self.simulation_settings.AU * (1 + eccentricity)
            a = semi_major_axis_au * self.simulation_settings.AU
            speed = math.sqrt(self.simulation_settings.G * sun_mass * (2/distance - 1/a))

        angle = math.radians(start_angle_deg)
        position = Vector2(distance * math.cos(angle), distance * math.sin(angle))

        # Tangiental velocity ( perpendicular to radius )
        velocity = Vector2(-speed * math.sin(angle), speed * math.cos(angle))

        self.orbit_simulator.spawn_object_hard(
            position,
            radius,
            mass,
            velocity,
            name
        )

    def spawn_planets(self):

        self.add_planet("Earth", 1.000, 0.0167, 5.9742e24, 15, 90, False)
        self.add_planet("Mercury", 0.387, 0.2056, 3.30e23, 10, 0, True)
        self.add_planet("Venus", 0.723, 0.0068, 4.8685e24, 10, 45, False)
        self.add_planet("Mars", 1.524, 0.0934, 6.39e23, 15, 135, True)
        self.add_planet("Jupiter", 5.203, 0.0489, 1.898e27, 40, 180, False)
        self.add_planet("Saturn", 9.537, 0.0539, 5.683e26, 35, 225, False)
        

    def start(self):
        if self.canvas is None:
            raise ValueError("orbitSim requires a Canvas to run orbital simulation")
        self.orbit_simulator = ObjectManager(
            self.canvas, 
            self.object_config, 
            self.simulation_settings,
            self.update_planet_info,
            self.clear_planet_info
        )
        self.orbit_simulator.spawn_sun()
                                     
        self.orbit_simulator.update_objects()



if __name__ == "__main__":
    print("Welcome to orbitSim")

    root = Tk()
    orbit_sim = OrbitSimulation(root)
    orbit_sim.start()
    root.mainloop()

    print("Exiting orbitSim")
