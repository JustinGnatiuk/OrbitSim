import math
from tkinter import Canvas, Tk, ttk, IntVar
from celestialobject import ObjectManager, Vector2, AU, G


WIDTH, HEIGHT = 1200, 675


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
        mass_label = ttk.Label(form_frame, text='Mass:', anchor='w', font=('Arial', 12))
        mass_label.grid(row=0, column=0, sticky='w', padx=(5,0), pady=5)
        mass_entry = ttk.Entry(form_frame, width=15)
        mass_entry.grid(row=0, column=1, sticky='w', padx=(5,0), pady=5)
        self.object_config['mass'] = mass_entry

        # Object initial velocity label and entry form
        initial_velocity = ttk.Label(form_frame, text="Initial Velocity: ", anchor='w', font=('Arial', 12))
        initial_velocity.grid(row=1, column=0, sticky='w', padx=(5,0), pady=5)
        initial_velocity_entry = ttk.Entry(form_frame, width=15)
        initial_velocity_entry.grid(row=1, column=1, sticky='w', padx=(5,0), pady=5)
        self.object_config['initial_velocity'] = initial_velocity_entry
        
        # Object tag label and entry form
        tag_label = ttk.Label(form_frame, text="Tag:", anchor='w', font=('Arial', 12))
        tag_label.grid(row=2, column=0, sticky='w', padx=(5,0), pady=5)
        tag_entry = ttk.Entry(form_frame, width=15)
        tag_entry.grid(row=2, column=1, sticky='w', padx=(5,0), pady=5)
        self.object_config['tag'] = tag_entry
        
        # Orbit Lines label and button
        orbit_var = IntVar()
        orbit_option = ttk.Checkbutton(form_frame, text="Draw Orbits ", variable=orbit_var)
        orbit_option.grid(row=3, column=0, sticky='w', padx=(5,0), pady=5)
        self.object_config['draw_orbit'] = orbit_var

        # Orbit pause/unpause button
        orbit_pause = ttk.Button(form_frame, text="Pause", command=self.toggle_pause)
        orbit_pause.config(command=lambda: self.toggle_pause(orbit_pause))
        orbit_pause.grid(row=3, column=1, sticky='w', padx=(5,0), pady=5)


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
            distance = semi_major_axis_au * AU * (1 - eccentricity)
            # speed at perihelion from vis-viva equation: v squared = GM(2/r - 1/a)
            a = semi_major_axis_au * AU # Convert to meters
            speed = math.sqrt(G * sun_mass * (2/distance - 1/a))
        else:
            # Aphelion distance = a(1+e)
            distance = semi_major_axis_au * AU * (1 + eccentricity)
            a = semi_major_axis_au * AU
            speed = math.sqrt(G * sun_mass * (2/distance - 1/a))

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

        

    def start(self):
        if self.canvas is None:
            raise ValueError("orbitSim requires a Canvas to run orbital simulation")
        self.orbit_simulator = ObjectManager(self.canvas, self.object_config)
        self.orbit_simulator.spawn_sun()
        # add earth by default for testing
        self.add_planet("Earth", 1.000, 0.0167, 5.9742e24, 12, 90, False)
        # add some of the other planets for testing
        self.add_planet("Mercury", 0.387, 0.2056, 3.30e23, 8, 0, True)
        self.add_planet("Venus", 0.723, 0.0068, 4.8685e24, 10, 45, False)
        self.add_planet("Mars", 1.524, 0.0934, 6.39e23, 10, 135, True)

        #self.orbit_simulator.spawn_object_hard(Vector2(-1 * AU, 0),
        #                                       15,
        #                                       5.9742 * 10**24,
        #                                       Vector2(0, 29.783 * 1000),
        #                                       "Earth"
        #                                       )
        ## add venus by default for testing
        #self.orbit_simulator.spawn_object_hard(Vector2(0.723 * AU, 0),
        #                                       10,
        #                                       4.8685 * 10**24,
        #                                       Vector2(0, -35.02 * 1000),
        #                                       "Venus"
        #                                       )
        ## add mercury by default for testing
        #self.orbit_simulator.spawn_object_hard(Vector2(0.387 * AU, 0),
        #                                       10,
        #                                       3.30 * 10**23,
        #                                       Vector2(0, -47.4 * 1000),
        #                                       "Mercury"
        #                                       )
        ## add Mars by default for testing
        #self.orbit_simulator.spawn_object_hard(Vector2(-1.524 * AU, 0),
        #                                       12,
        #                                       6.39 * 10**23,
        #                                       Vector2(0, 24.077 * 1000),
        #                                       "Mars"
        #                                       )
        self.orbit_simulator.update_objects()



if __name__ == "__main__":
    print("Welcome to orbitSim")

    root = Tk()
    orbit_sim = OrbitSimulation(root)
    orbit_sim.start()
    root.mainloop()

    print("Exiting orbitSim")
