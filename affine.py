import tkinter
from typing import Any
import numpy as np
from tkinter import simpledialog
from geometry import Point, BaseCanvas, Number, PointType, LineType, Shape

WIDTH = 300
HEIGHT = 300


class InteractiveCanvas(BaseCanvas):
    def __init__(self, width: int, height: int) -> None:
        super().__init__(width, height)
        self.old_point: Point | None = None

    def __add__(self, shape: Shape) -> "InteractiveCanvas":
        super().__add__(shape)
        return self

    def clear(self) -> None:
        self.old_point = None
        return super().clear()

def clear_canvas(
    tk_canvas: tkinter.Canvas, canvas: InteractiveCanvas
) -> None:
    canvas.clear()
    tk_canvas.delete("all")

def click_event(
    event: tkinter.Event, tk_canvas: tkinter.Canvas, canvas: InteractiveCanvas
) -> None:

    if event.x < 0 or event.x > canvas.width or event.y < 0 or event.y > canvas.height:
        return

    if event.num == 1:  # Left mouse button
        x, y = event.x, event.y
        point = Point(x, y)
        canvas += point
        draw_canvas(tk_canvas, canvas)

        if canvas.old_point:
            draw_line(
                tk_canvas,
                canvas,
                canvas.old_point.x,
                canvas.old_point.y,
                point.x,
                point.y,
            )
        canvas.old_point = point

    elif event.num == 3:  # Right mouse button
        canvas.old_point = None

    print(f"Canvas state: {canvas}")


def draw_line(
    tk_canvas: tkinter.Canvas,
    canvas: InteractiveCanvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> None:
    if not (
        0 <= x1 <= canvas.width
        and 0 <= y1 <= canvas.height
        and 0 <= x2 <= canvas.width
        and 0 <= y2 <= canvas.height
    ):
        raise ValueError("Coordinates must be within the canvas dimensions.")

    dx = x2 - x1
    dy = y2 - y1

    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        return

    x_inc = dx / steps
    y_inc = dy / steps

    for i in range(steps + 1):
        x = int(x1 + i * x_inc)
        y = int(y1 + i * y_inc)
        canvas += Point(x, y)

    draw_canvas(tk_canvas, canvas)


def draw_canvas(tk_canvas: tkinter.Canvas, canvas: InteractiveCanvas) -> None:
    tk_canvas.delete("all")
    for x, y in canvas.points:
        tk_canvas.create_line(x, y, x + 1, y + 1, fill="black")


def with_point_selection(func: Any) -> Any:
    def wrapper(tk_canvas: tkinter.Canvas, canvas: InteractiveCanvas, *args: Any, **kwargs: Any) -> None:
        coords = {}

        def on_click(event: tkinter.Event) -> None:
            coords["x"] = event.x
            coords["y"] = event.y
            tk_canvas.delete("msg")
            tk_canvas.unbind("<Button-1>", bind_id)
            tk_canvas.bind(
                "<Button-1>", lambda event: click_event(event, tk_canvas, canvas)
            )
            center = Point(coords["x"], coords["y"])
            func(tk_canvas, canvas, center, *args, **kwargs)

        tk_canvas.addtag_withtag(
            "msg",
            tk_canvas.create_text(
                canvas.width // 2,
                20,
                text="Кликните для выбора точки",
                fill="red",
                font=("Arial", 16),
            ),
        )
        bind_id = tk_canvas.bind("<Button-1>", on_click)

    return wrapper


def apply_transformation(tk_canvas: tkinter.Canvas, canvas: InteractiveCanvas) -> None:
    dx = simpledialog.askfloat(
        "Transformation", "Введите dx (смещение по X):", parent=tk_canvas
    )
    dy = simpledialog.askfloat(
        "Transformation", "Введите dy (смещение по Y):", parent=tk_canvas
    )
    if dx is None or dy is None:
        return

    matrix = np.array([[1, 0, dx], [0, 1, dy], [0, 0, 1]])

    canvas.transform(matrix)
    draw_canvas(tk_canvas, canvas)


def apply_rotation(
    tk_canvas: tkinter.Canvas, canvas: InteractiveCanvas, center: Point
) -> None:
    angle = simpledialog.askfloat(
        "Transformation", "Введите угол поворота (в градусах):", parent=tk_canvas
    )
    if angle is None:
        return

    radians = np.radians(angle)
    cos_a = np.cos(radians)
    sin_a = np.sin(radians)

    translation_to_origin = np.array([[1, 0, -center.x], [0, 1, -center.y], [0, 0, 1]])
    rotation_matrix = np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]])
    translation_back = np.array([[1, 0, center.x], [0, 1, center.y], [0, 0, 1]])

    matrix = translation_back @ rotation_matrix @ translation_to_origin

    canvas.transform(matrix)
    draw_canvas(tk_canvas, canvas)


@with_point_selection
def apply_rotation_around_point(
    tk_canvas: tkinter.Canvas, canvas: InteractiveCanvas, center: Point
) -> None:
    apply_rotation(tk_canvas, canvas, center)


def apply_scaling(
    tk_canvas: tkinter.Canvas, canvas: InteractiveCanvas, center: Point
) -> None:
    sx = simpledialog.askfloat(
        "Transformation",
        "Введите коэффициент масштабирования по X (sx):",
        parent=tk_canvas,
    )
    sy = simpledialog.askfloat(
        "Transformation",
        "Введите коэффициент масштабирования по Y (sy):",
        parent=tk_canvas,
    )
    if sx is None or sy is None:
        return

    translation_to_origin = np.array([[1, 0, -center.x], [0, 1, -center.y], [0, 0, 1]])
    scaling_matrix = np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1]])
    translation_back = np.array([[1, 0, center.x], [0, 1, center.y], [0, 0, 1]])

    matrix = translation_back @ scaling_matrix @ translation_to_origin

    canvas.transform(matrix)
    draw_canvas(tk_canvas, canvas)


@with_point_selection
def apply_scaling_around_point(
    tk_canvas: tkinter.Canvas, canvas: InteractiveCanvas, center: Point
) -> None:
    apply_scaling(tk_canvas, canvas, center)


if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("Холст")
    root.geometry(f"{WIDTH}x{HEIGHT}")

    canvas = InteractiveCanvas(WIDTH, HEIGHT)
    tk_canvas = tkinter.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
    tk_canvas.pack()

    tk_canvas.bind("<Button-1>", lambda event: click_event(event, tk_canvas, canvas))
    tk_canvas.bind("<Button-3>", lambda event: click_event(event, tk_canvas, canvas))

    menubar = tkinter.Menu(root)
    file_menu = tkinter.Menu(menubar, tearoff=0)
    edit_menu = tkinter.Menu(menubar, tearoff=0)

    file_menu.add_command(label="Выйти", command=root.quit)
    menubar.add_cascade(label="Файл", menu=file_menu)

    edit_menu.add_command(
        label="Применить сдвиг", command=lambda: apply_transformation(tk_canvas, canvas)
    )
    edit_menu.add_command(
        label="Применить поворот",
        command=lambda: apply_rotation(
            tk_canvas, canvas, Point(WIDTH // 2, HEIGHT // 2)
        ),
    )
    edit_menu.add_command(
        label="Повернуть вокруг точки",
        command=lambda: apply_rotation_around_point(tk_canvas, canvas),
    )
    edit_menu.add_command(
        label="Применить масштабирование",
        command=lambda: apply_scaling(
            tk_canvas, canvas, Point(WIDTH // 2, HEIGHT // 2)
        ),
    )
    edit_menu.add_command(
        label="Масштабировать вокруг точки",
        command=lambda: apply_scaling_around_point(tk_canvas, canvas),
    )
    edit_menu.add_separator()
    edit_menu.add_command(
        label="Очистить холст", command=lambda: clear_canvas(tk_canvas, canvas)
    )
    menubar.add_cascade(label="Правка", menu=edit_menu)

    root.config(menu=menubar)

    root.mainloop()
