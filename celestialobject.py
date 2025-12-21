import math
from tkinter import Canvas

class Vector2:
    def __init__(self, x, y) -> None:
        self.x, self.y = x, y



class CelestialObject:
    def __init__(self, origin: Vector2, canvas: Canvas, radius: int, tag: str,) -> None:
        self.center = Vector2(origin.x, origin.y)
        self.canvas = canvas
        self.radius = radius
        self.color = "white"
        self.tag = tag

    def draw(self):
        x1 = self.center.x - self.radius
        y1 = self.center.y - self.radius
        x2 = self.center.x + self.radius
        y2 = self.center.y + self.radius
        self.canvas.create_oval(x1, y1, x2, y2, fill="black", outline=self.color)



class ObjectManager:
    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas
        self.celestialObjects = []

        self.canvas.bind("<Button-1>", self.spawn_object)

    # Spawn Celestial Object ( a Circle )
    def spawn_object(self, event):
        new_object = CelestialObject(
            Vector2(event.x, event.y), 
            self.canvas,
            10,
            "object"
        )
        self.celestialObjects.append(new_object)
        new_object.draw()