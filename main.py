from tkinter import Canvas, Tk, ttk
from celestialobject import ObjectManager, Vector2, AU


WIDTH, HEIGHT = 1200, 675


class OrbitSimulation:
    def __init__(self,root):
        self.root = root
        self.root.title("Orbit Simulation - github.com/JustinGnatiuk")
        self.root.resizable(0,0)
        self.canvas = None
        self.object_manager = None
        self.object_config = []

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
        mass_label.grid(row=0, column=0, sticky='w', padx=(5, 0), pady=5)
        mass_entry = ttk.Entry(form_frame, width=15)
        mass_entry.grid(row=0, column=1, sticky='w', padx=(5, 0), pady=5)
        self.object_config.append(mass_entry)

        # Object tag label and entry form
        tag_label = ttk.Label(form_frame, text="Tag:", anchor='w', font=('Arial', 12))
        tag_label.grid(row=1, column=0, sticky='w', padx=(5, 0), pady=5)
        tag_entry = ttk.Entry(form_frame, width=15)
        tag_entry.grid(row=1, column=1, sticky='w', padx=(5, 0), pady=5)
        self.object_config.append(tag_entry)

        
    def start(self):
        if self.canvas is None:
            raise ValueError("orbitSim requires a Canvas to run orbital simulation")
        self.orbit_simulator = ObjectManager(self.canvas, self.object_config)
        self.orbit_simulator.spawn_sun()
        # add earth by default for testing
        self.orbit_simulator.spawn_object_hard(Vector2(-1 * AU, 0) , 15,  5.9742 * 10**24, "Earth")
        self.orbit_simulator.update_objects()



if __name__ == "__main__":
    print("Welcome to orbitSim")

    root = Tk()
    orbit_sim = OrbitSimulation(root)
    orbit_sim.start()
    root.mainloop()

    print("Exiting orbitSim")
