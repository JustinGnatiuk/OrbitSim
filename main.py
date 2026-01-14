import math
import tkinter as tk
from tkinter import Canvas, Tk, ttk, IntVar
from celestialobject import ObjectManager, Vector2


WIDTH, HEIGHT = 1200, 675

# Object for Simulation Settings and Constants
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

# Main Orbit Simulation Object
class OrbitSimulation:
    def __init__(self,root):
        self.root = root
        self.root.title("Orbit Simulation - github.com/JustinGnatiuk")
        self.root.resizable(0,0)
        self.canvas = None
        self.object_manager = None
        # Config object for planets
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

        # Populate Side Configuration Bar
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

        # Populate form input container

        # Object mass label and entry form
        mass_label = ttk.Label(form_frame, text='Mass (kg):', anchor='w', font=('Arial', 12))
        mass_label.grid(row=0, column=0, sticky='w', padx=(5,0), pady=5)
        mass_entry = ttk.Entry(form_frame, width=15)
        mass_entry.grid(row=0, column=1, sticky='w', padx=(5,0), pady=5)

        # Set object config mass to mass entry
        self.object_config['mass'] = mass_entry

        # Object initial velocity in x direction label and entry form
        initial_velocity_x = ttk.Label(form_frame, text="Velocity x (km/s): ", anchor='w', font=('Arial', 12))
        initial_velocity_x.grid(row=1, column=0, sticky='w', padx=(5,0), pady=5)
        initial_velocity_x_entry = ttk.Entry(form_frame, width=15)
        initial_velocity_x_entry.grid(row=1, column=1, sticky='w', padx=(5,0), pady=5)

        # Set object config initial_velocity_x to initial velocity x entry
        self.object_config['initial_velocity_x'] = initial_velocity_x_entry

        # Object initial velocity in y direction label and entry form
        initial_velocity_y = ttk.Label(form_frame, text="Velocity y (km/s): ", anchor='w', font=('Arial', 12))
        initial_velocity_y.grid(row=2, column=0, sticky='w', padx=(5,0), pady=5)
        initial_velocity_y_entry = ttk.Entry(form_frame, width=15)
        initial_velocity_y_entry.grid(row=2, column=1, sticky='w', padx=(5,0), pady=5)

        # Set object config initial_velocity_y to initial velocity y entry
        self.object_config['initial_velocity_y'] = initial_velocity_y_entry

        # Object radius label and entry form
        radius_label = ttk.Label(form_frame, text="Radius (pixels):", anchor='w', font=('Arial', 12))
        radius_label.grid(row=3, column=0, sticky='w', padx=(5,0), pady=5)
        radius_entry = ttk.Entry(form_frame, width=15)
        radius_entry.grid(row=3, column=1, sticky='w', padx=(5,0), pady=5)

        # Set object config radius to radius entry
        self.object_config['radius'] = radius_entry
        
        # Object tag label and entry form
        tag_label = ttk.Label(form_frame, text="Tag:", anchor='w', font=('Arial', 12))
        tag_label.grid(row=4, column=0, sticky='w', padx=(5,0), pady=5)
        tag_entry = ttk.Entry(form_frame, width=15)
        tag_entry.grid(row=4, column=1, sticky='w', padx=(5,0), pady=5)

        # Set object config tag to tag entry
        self.object_config['tag'] = tag_entry
        
        # Orbit Lines label and button
        orbit_var = IntVar()
        orbit_option = ttk.Checkbutton(form_frame, text="Draw Orbits ", variable=orbit_var)
        orbit_option.grid(row=5, column=0, sticky='w', padx=(5,0), pady=5)

        # Set object config draw_orbit flag to state of checkbox ( 1 or 0 )
        self.object_config['draw_orbit'] = orbit_var

        # Orbit pause/unpause button
        orbit_pause = ttk.Button(form_frame, text="Pause", command=lambda: self.toggle_pause(orbit_pause))
        orbit_pause.grid(row=5, column=1, sticky='w', padx=(5,0), pady=5)

        # info button
        info_button = ttk.Button(form_frame, text="Show Info", command=self.show_info)
        info_button.grid(row=6, column=0, sticky='w', padx=(5,0), pady=5)

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
        zoom_scale.grid(row=7, column=0, sticky='w', padx=(5,0), pady=5, columnspan=2)

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
        speed_scale.grid(row=8, column=0, sticky='w', padx=(5,0), pady=5, columnspan=2)

        # Create a frame specifically for planet info in bottom right
        info_frame = ttk.LabelFrame(side_config, text="Planet Information", padding="10", width=100)
        info_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10, expand=True)

        # Create labels to display planet information
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

        # Object radius in pixels
        self.info_labels['radius'] = ttk.Label(info_frame, text="Radius: 0")
        self.info_labels['radius'].pack(anchor=tk.W, pady=(5, 0))

        # Clear planets button
        clear_planets = ttk.Button(form_frame, text="Clear Planets", command=self.clear_planets)
        clear_planets.grid(row=9, column=0, sticky='w', padx=(5,0), pady=5)

        # Spawn planets button
        spawn_planets = ttk.Button(form_frame, text="Spawn Planets", command=self.spawn_planets)
        spawn_planets.grid(row=9, column=1, sticky='w', padx=(5,0), pady=5)

        # Canvas x,y arrows
        self.canvas.create_line(10, 10, 10, 50, arrow=tk.LAST, width=1, fill="white")
        self.canvas.create_line(10, 10, 50, 10, arrow=tk.LAST, width=1, fill="white")
        self.canvas.create_text(
                20, 50,                     
                text="y",  
                font=("Arial", 8, "bold italic"),  
                fill="white",                                              
            )
        self.canvas.create_text(
                50, 20,                     
                text="x",  
                font=("Arial", 8, "bold italic"),  
                fill="white",                                              
            )

    def update_planet_info(self, planet):
        
        # set selected planet of objectManager class
        self.orbit_simulator.selected_planet = planet

        # Set info labels to planet properties
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

        self.info_labels['radius'].config(text=f"Radius: {planet.base_radius} pixels")

    def clear_planet_info(self):

        # clear selected planet of objectManager class
        self.orbit_simulator.selected_planet = None

        # Reset info labels back to default state
        self.info_labels['tag'].config(text="Tag: None")
        self.info_labels['mass'].config(text="Mass: 0.0")
        self.info_labels['velocity'].config(text="Velocity: (0.0, 0.0)")
        self.info_labels['position'].config(text="Position: (0.0, 0.0)")
        self.info_labels['distance'].config(text="Distance from Sun: 0.0")

    def update_zoom(self, value):
        
        # update simulation settings zoom value
        self.simulation_settings.zoom = float(value)

        # remove all orbit lines and redraw planets
        for planet in self.orbit_simulator.celestialObjects:
            self.canvas.delete(f"{planet.tag}_orbit")
            planet.orbit_line_id = None
            planet.orbit = []
            planet.update_radius()
            planet.update_screen_position()
            planet.draw()
            
    def show_info(self):
        
        # If window is already open, reopen it
        if( hasattr(self, 'info_window') and self.info_window.winfo_exists() ):
            self.info_window.lift()
            self.info_window.focus_force()
            return

        # Build info window
        self.info_window = tk.Toplevel(self.root)
        self.info_window.title("Simulation Help")
        self.info_window.geometry("500x450")
        self.info_window.transient(self.root)
        self.info_window.resizable(0,0)

        tk.Label(self.info_window, text="Python Orbit Simulator", font=("Arial", 12, "bold")).pack(pady=10)

        text_frame = tk.Frame(self.info_window)
        text_frame.pack(fill="both", expand=True, padx=20)

        text_content = tk.Text(text_frame, wrap="word", height=10)
        text_content.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=text_content.yview)
        scrollbar.pack(side="right", fill="y")
        text_content.config(yscrollcommand=scrollbar.set)

        information = """Welcome to OrbitSim
This program simulates the orbits of planets around our sun ( decently )
The simulation is in 2D space though, so if you're trying to put a man on the moon with this,
you may need to look elsewhere.

Here's some instructions to get going,

--To Spawn a Planet--
1. Fill out the mass in kg
2. Give it an x velocity in km/s
3. Give it a y velocity in km/s
4. Give it a radius in pixels ( I suggest between 5-25 )
5. Give it a name ( tag )

NOTE: values can be expressed in scientific or E notation
ex : [ 1.5x10^24 ] or [ 1.5e24 ]

SECOND NOTE: Radius is scaled with zoom scale. 
Base radius is displayed in info window.
This is so the planets will "shrink" as you zoom out
Radius = Base_Radius x zoom scale

Orbits can be chaotic. If you give your planet insufficient mass or velocity parameters,
it's very likely that it will fly into the sun and shoot out of the solar system due to its
drastic velocity change due to it's proximity to the sun.

If you're having trouble generating a planet with a stable orbit around the sun, go ahead and 
click the "Spawn Planets" button. This will generate realistic orbits for Mercury, Venus, Earth,
Mars, Jupiter and Saturn.

You can clear the planets with the "Clear Planets" button.

Adjust the zoom scale ( 0.1 to 2.5 ) to zoom out, in order to see Jupiter and Saturn.
You can also zoom in as well obviously.
I didn't implement Uranus or Neptune, they are way too far away from the sun and the scaling
for the canvas was complex. A better version of this program would implement that and have 
better scaling.

You can click on any planet to view its planet information in the bottom right. You should be
able to use these values for reference to generate stable orbits for your planet.

You can adjust the speed of the simulation with the speed slider. This controls the delay of 
the loop that handles all of the movement and physics. 
It ranges from 10ms ( Very Fast ) to 100ms ( Very Slow )

Select the "Draw Orbits" checkbox to draw orbits for the planets for better visualization.

Must I explain what the Pause/Continue button does? (:

Thank you for checking out my simulator!

-Jaygnat


        """

        text_content.insert("1.0", information)
        text_content.config(state="disabled")

        tk.Button(self.info_window, text="Close", command=self.info_window.destroy).pack(pady=10)

    def clear_planets(self):
        
        # Call clear planets function in objectManager class
        self.orbit_simulator.clear_planets()
            

    def update_speed(self, value):
        self.simulation_settings.SPEED = value

    def toggle_pause(self, pause_button):

        # Pause Value 0 : Not paused
        # Pause Value 1 : Paused
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

        # Spawn planet with calculated properties
        self.orbit_simulator.spawn_object_hard(
            position,
            radius,
            mass,
            velocity,
            name
        )

    def spawn_planets(self):

        # Spawn Mercury, Venus, Earth, Mars, Jupiter, Saturn
        self.add_planet("Earth", 1.000, 0.0167, 5.9742e24, 15, 90, False)
        self.add_planet("Mercury", 0.387, 0.2056, 3.30e23, 10, 0, True)
        self.add_planet("Venus", 0.723, 0.0068, 4.8685e24, 10, 45, False)
        self.add_planet("Mars", 1.524, 0.0934, 6.39e23, 15, 135, True)
        self.add_planet("Jupiter", 5.203, 0.0489, 1.898e27, 40, 180, False)
        self.add_planet("Saturn", 9.537, 0.0539, 5.683e26, 35, 225, False)
        
    # Begin Simulation
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

    # Build root window and initialize OrbitSimulation object with root window
    root = Tk()
    orbit_sim = OrbitSimulation(root)
    orbit_sim.start()
    root.mainloop()

    print("Exiting orbitSim")
