import tkinter

WIDTH = 300
HEIGHT = 300

class RGB:
    def __init__(self, r: int, g: int, b: int) -> None:
        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            raise ValueError("RGB values must be in the range 0-255.")
        
        self.r = r
        self.g = g
        self.b = b
    
    def __repr__(self) -> str:
        return f"RGB({self.r}, {self.g}, {self.b})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, RGB):
            return False
        return self.r == other.r and self.g == other.g and self.b == other.b
    
    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)

class Pixel:
    def __init__(self, x: float, y: float, color: RGB = RGB(0, 0, 0)) -> None:

        self.x = x
        self.y = y
        self.color = color
    
    def __repr__(self) -> str:
        return f"Pixel({self.x}, {self.y}, color={self.color})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Pixel):
            return False
        return self.x == other.x and self.y == other.y
    
    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)
    
class Canvas:
    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive values.")
        
        self.width = width
        self.height = height
        self.pixels: list[Pixel] = []

    def __repr__(self) -> str:
        return f"Canvas({self.width}, {self.height}, pixels_count={len(self.pixels)})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Canvas):
            return False
        return (self.width == other.width and 
                self.height == other.height and 
                self.pixels == other.pixels)
    
    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)
    
    def __add__(self, pixel: Pixel) -> "Canvas":
        if not isinstance(pixel, Pixel):
            raise TypeError("Only Pixel instances can be added to Canvas.")
        
        if not (0 <= pixel.x <= self.width and 0 <= pixel.y <= self.height):
            raise ValueError("Pixel coordinates must be within the canvas dimensions.")
        
        self.pixels.append(pixel)
        return self
    
def draw_triangle(canvas: Canvas, p1: Pixel, p2: Pixel, p3: Pixel) -> None:
    if not all(isinstance(p, Pixel) for p in [p1, p2, p3]):
        raise TypeError("All vertices must be pixel instances.")
    
    for p in [p1, p2, p3]:
        if not (0 <= p.x <= canvas.width and 0 <= p.y <= canvas.height):
            raise ValueError("Triangle vertices must be within the canvas dimensions.")
        
        canvas += Pixel(p.x, p.y, p.color)

    for i in range(3):
        p_start = [p1, p2, p3][i]
        p_end = [p1, p2, p3][(i + 1) % 3]
        
        x1, y1 = p_start.x, p_start.y
        x2, y2 = p_end.x, p_end.y
        
        dx = x2 - x1
        dy = y2 - y1
        steps = int(max(abs(dx), abs(dy)))
        
        if steps == 0:
            continue
        
        x_inc = dx / steps
        y_inc = dy / steps
        
        x, y = x1, y1
        for _ in range(steps + 1):
            canvas += Pixel(round(x), round(y), p_start.color)
            x += x_inc
            y += y_inc

def area(p1: Pixel, p2: Pixel, p3: Pixel) -> float:
    return ((p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y)) / 2.0

def fill_triangle(canvas: Canvas, p1: Pixel, p2: Pixel, p3: Pixel) -> None:
    if not all(0 <= px < canvas.width and 0 <= py < canvas.height for px, py in [(p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y)]):
        raise ValueError("Triangle vertices must be within the canvas dimensions.")
    
    xmin = min(p1.x, p2.x, p3.x)
    ymin = min(p1.y, p2.y, p3.y)
    xmax = max(p1.x, p2.x, p3.x)
    ymax = max(p1.y, p2.y, p3.y)

    S = area(p1, p2, p3)

    for x in range(int(xmin), int(xmax) + 1):
        for y in range(int(ymin), int(ymax) + 1):
            p = Pixel(x, y)
            S1 = area(p, p2, p3)
            S2 = area(p1, p, p3)
            S3 = area(p1, p2, p)
            u = S1 / S
            v = S2 / S
            w = S3 / S
            if u < 0 or v < 0 or w < 0:
                continue

            r = int(u * p1.color.r + v * p2.color.r + w * p3.color.r)
            g = int(u * p1.color.g + v * p2.color.g + w * p3.color.g)
            b = int(u * p1.color.b + v * p2.color.b + w * p3.color.b)
            canvas += Pixel(x, y, RGB(r, g, b))

if __name__ == "__main__":
    canvas = Canvas(WIDTH, HEIGHT)
    p1 = Pixel(50, 50, RGB(255, 0, 0))
    p2 = Pixel(250, 5, RGB(0, 255, 0))
    p3 = Pixel(150, 250, RGB(0, 0, 255))
    draw_triangle(canvas, p1, p2, p3)

    root = tkinter.Tk()
    canvas_widget = tkinter.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
    canvas_widget.pack()

    fill_triangle(canvas, p1, p2, p3)

    for pixel in canvas.pixels:
        r = 1
        x = pixel.x
        y = pixel.y
        color = f"#{pixel.color.r:02x}{pixel.color.g:02x}{pixel.color.b:02x}"
        canvas_widget.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill=color, outline=""
        )

    print(canvas)
    
    root.mainloop()