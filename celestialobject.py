import math
from tkinter import Canvas

class Vector2:
    def __init__(self, x, y) -> None:
        self.x, self.y = x, y



class CelestialObject:
    def __init__(self, origin: Vector2, canvas: Canvas, radius: int, tag: str,) -> None:
        self.canvas = canvas
        self.radius = radius
        self.color = "white"
        self.tag = tag

    def draw(self):
        return


class ObjectManager:
    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas
        self.celestialobjects = []

        self.canvas.bind("<Button-1>", self.spawn_object)

    # Spawn Celestial Object ( a Circle )
    def spawn_object(self, event):
        radius = 10
        x1 = event.x - radius
        y1 = event.y - radius
        x2 = event.x + radius
        y2 = event.y + radius
        self.canvas.create_oval(x1, y1, x2, y2, fill="black", outline="white")