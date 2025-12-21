from tkinter import Canvas, Tk, ttk


WIDTH, HEIGHT = 1200, 675


class OrbitSimulation:
    def __init__(self,root):
        self.root = root
        self.root.title("Orbit Simulation - github.com/JustinGnatiuk")
        self.root.resizable(0,0)
        self.root.minsize(WIDTH,HEIGHT)
        self.root.maxsize(WIDTH,HEIGHT)
        self.canvas = None
        self.orbit_manager = None

        self.build_gui()

    def build_gui(self):

        # Create Main Container
        main_container = ttk.Frame(self.root, width=WIDTH, height=HEIGHT)
        main_container.pack(fill='both', expand=False)
        main_container.pack_propagate(False)

        # Create Simulation Canvas
        self.canvas = Canvas(main_container, width=WIDTH-250, height=HEIGHT, bg='black')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Create Side Configuration Bar
        side_config = ttk.Frame(main_container, width=250)
        side_config.pack(side='right', fill='y', expand=False)
        side_config.pack_propagate(False)

    def start(self):
        if self.canvas is None:
            raise ValueError("orbitSim requires a Canvas to run orbital simulation")



if __name__ == "__main__":
    print("Welcome to orbitSim")

    root = Tk()
    orbit_sim = OrbitSimulation(root)
    orbit_sim.start()
    root.mainloop()

    print("Exiting orbitSim")
