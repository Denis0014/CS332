# import math
from typing import Callable
import tkinter

WIDTH = 300
HEIGHT = 300

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class Canvas:
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
        self.points: list[Point] = []
        self.xmin = float('inf')
        self.xmax = float('-inf')
        self.ymin = float('inf')
        self.ymax = float('-inf')
        
    def plot(self, func: Callable[[float], float], xmin: float = 0, xmax: float = 10, step: float = 0.1):
        x = xmin
        self.xmin = xmin
        self.xmax = xmax

        self.ymin = func(x)
        self.ymax = self.ymin

        while x <= xmax:
            y = func(x)
            
            if y < self.ymin:
                self.ymin = y
            elif y > self.ymax:
                self.ymax = y

            self.points.append(Point(x, y))

            x += step

    def __repr__(self):
        return f"Canvas({self.width}, {self.height}, points={self.points})"

def draw(canvas_widget: tkinter.Canvas, canvas: Canvas, width: int, height: int):
    canvas_widget.delete('all')
    x_old = None
    y_old = None

    for i in range(0, len(canvas.points) - 1):
        r = 2
        y = (canvas.points[i].y - canvas.ymin) / (canvas.ymax - canvas.ymin) * height
        y = height - y
        x = (canvas.points[i].x - canvas.xmin) / (canvas.xmax - canvas.xmin) * width

        canvas_widget.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill="blue", outline=""
        )
        if x_old is not None and y_old is not None:
            canvas_widget.create_line(
                x_old, y_old, x, y, fill="blue"
            )
        x_old = x
        y_old = y

if __name__ == "__main__":
    def func(x: float) -> float:
        return x ** 2

    canvas = Canvas(WIDTH, HEIGHT)
    canvas.plot(func, -10, 10)

    root = tkinter.Tk()
    root.title("Plot")

    canvas_widget = tkinter.Canvas(root, width=canvas.width, height=canvas.height, bg="white")
    canvas_widget.pack(fill="both", expand=True)

    draw(canvas_widget, canvas, WIDTH, HEIGHT)

    resize_job = None

    def on_window_resize(event: tkinter.Event) -> None:
        global resize_job
        if resize_job is not None:
            root.after_cancel(resize_job)
        resize_job = root.after(100, lambda: draw(canvas_widget, canvas, event.width, event.height))

    root.bind("<Configure>", on_window_resize)

    root.mainloop()
