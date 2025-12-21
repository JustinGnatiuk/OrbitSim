from tkinter import Canvas, Tk, ttk
from celestialobject import ObjectManager


WIDTH, HEIGHT = 1200, 675


class OrbitSimulation:
    def __init__(self,root):
        self.root = root
        self.root.title("Orbit Simulation - github.com/JustinGnatiuk")
        self.root.resizable(0,0)
        self.canvas = None
        self.object_manager = None

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

    def start(self):
        if self.canvas is None:
            raise ValueError("orbitSim requires a Canvas to run orbital simulation")
        self.orbit_simulator = ObjectManager(self.canvas)



if __name__ == "__main__":
    print("Welcome to orbitSim")

    root = Tk()
    orbit_sim = OrbitSimulation(root)
    orbit_sim.start()
    root.mainloop()

    print("Exiting orbitSim")
