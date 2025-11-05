import tkinter
import numpy as np
from typing import List, Sequence
from geometry import Shape, PointType, Point, Line, BaseCanvas

WIDTH = 300
HEIGHT = 300


class TkinterCanvas(BaseCanvas):
    def __init__(self, width: int = WIDTH, height: int = HEIGHT) -> None:
        super().__init__(width, height)

        self.polygons: List[List[PointType]] = []
        self.intersection_points: dict[PointType, List[PointType]] = {}
        self.inner_intersection_points: dict[PointType, List[PointType]] = {}

        self.tk_canvas = tkinter.Canvas(
            width=self.width, height=self.height, bg="white"
        )
        self.tk_canvas.pack()

    def make_points(self, points: Sequence[PointType]) -> None:
        for point in points:
            self += point

    def make_lines(self, lines: Sequence[Line]) -> None:
        for line in lines:
            if line.start == line.end:
                continue

            self += line

    def make_polygon(self, points: List[PointType]) -> None:        
        if len(points) < 3:
            raise ValueError("A polygon must have at least three points.")
        
        self.polygons.append(points)

    def clear(self) -> None:
        super().clear()
        self.lines.clear()
        self.intersection_points.clear()

    def transform(self, matrix: np.ndarray) -> None:
        if matrix.shape != (3, 3):
            raise ValueError("Transformation matrix must be 3x3.")
        if np.linalg.det(matrix) == 0:
            raise ValueError("Transformation matrix must be invertible (non-singular).")

        self.points.clear()
        self.grid_matrix = np.zeros((self.height, self.width), dtype=bool)

        for i in range(len(self.lines)):
            line = self.lines[i]
            start_vec = np.array([line.start.x, line.start.y, 1])
            end_vec = np.array([line.end.x, line.end.y, 1])
            new_start_vec = matrix @ start_vec
            new_end_vec = matrix @ end_vec

            x0, y0 = int(new_start_vec[0]), int(new_start_vec[1])
            x1, y1 = int(new_end_vec[0]), int(new_end_vec[1])

            point1 = Point(x0, y0)
            point2 = Point(x1, y1)
            line.start = point1
            line.end = point2

            self.lines[i] = line
            self += point1
            self += point2

            if 0 <= x0 < self.width and 0 <= y0 < self.height:
                self.grid_matrix[y0, x0] = True
            if 0 <= x1 < self.width and 0 <= y1 < self.height:
                self.grid_matrix[y1, x1] = True

    def __add__(self, shape: Shape) -> "TkinterCanvas":
        super().__add__(shape)
        return self
    
    def __sub__(self, point: PointType) -> "TkinterCanvas":
        super().__sub__(point)

        for i, line in enumerate(self.lines):
            p1, p2 = line
            if point == p1 or point == p2:
                del self.lines[i]
                break

        return self
    
    @staticmethod
    def get_lines_intersection(p1: PointType, p2: PointType, p3: PointType, p4: PointType) -> PointType | None:
        denom = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
        if denom == 0:
            return None

        x_num = (p1.x * p2.y - p1.y * p2.x) * (p3.x - p4.x) - (p1.x - p2.x) * (p3.x * p4.y - p3.y * p4.x)
        y_num = (p1.x * p2.y - p1.y * p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x * p4.y - p3.y * p4.x)

        x = x_num / denom
        y = y_num / denom

        if (
            min(p1.x, p2.x) <= x <= max(p1.x, p2.x)
            and min(p1.y, p2.y) <= y <= max(p1.y, p2.y)
            and min(p3.x, p4.x) <= x <= max(p3.x, p4.x)
            and min(p3.y, p4.y) <= y <= max(p3.y, p4.y)
        ):
            point = Point(x, y)
            point["lines"] = [ (p1, p2), (p3, p4) ]
            return point

        return None

    def checkIfPointWithin(self, point: PointType, polygon: List[PointType]) -> bool:
        x = point.x
        y = point.y

        inside = False
        for i in range(len(polygon)):
            xi, yi = polygon[i]
            xj, yj = polygon[(i - 1) % len(polygon)]

            if ((yi > y) != (yj > y)) and (x <= (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside

        print(f"{point} within polygon: {inside}")

        return inside

    def make_intersection_points(self) -> None:
        for i in range(len(self.lines)):
            for j in range(i + 1, len(self.lines)):
                p1, p2 = self.lines[i]
                p3, p4 = self.lines[j]
                intersection = self.get_lines_intersection(p1, p2, p3, p4)
                if intersection:
                    self += intersection
                    self.intersection_points.setdefault(intersection, []).extend([p1, p2, p3, p4])
                    if not (p1 == p2 or p3 == p4 or p1 == p3 or p1 == p4 or p2 == p3 or p2 == p4):
                        self.inner_intersection_points.setdefault(intersection, []).extend([p1, p2, p3, p4])

    def figure_intersections(self) -> List[PointType]:
        if not self.intersection_points:
            self.make_intersection_points()

        if not self.polygons:
            raise ValueError("No polygons defined on the canvas.")

        figure_points = list[PointType]()
        polygon_points = self.polygons[0]
        other_polygon = self.polygons[1]
        
        for point in polygon_points:
            if self.checkIfPointWithin(point, other_polygon):
                figure_points.append(point)          
        
        for point in other_polygon:
            if self.checkIfPointWithin(point, polygon_points):
                figure_points.append(point)

        figure_points.extend(self.inner_intersection_points.keys())
        return figure_points    

if __name__ == "__main__":
    canvas = TkinterCanvas(WIDTH, HEIGHT)
    p1 = Point(50, 120)
    p2 = Point(250, 120)
    p3 = Point(150, 220)

    canvas += p1
    canvas += p2
    canvas += p3

    canvas += Line(p1, p2)
    canvas += Line(p2, p3)
    canvas += Line(p3, p1)
    canvas.make_polygon([p1, p2, p3])

    p4 = Point(100, 200)
    p5 = Point(200, 200)
    p6 = Point(150, 70)
    p7 = Point(150, 250)

    canvas += p4
    canvas += p5
    canvas += p6
    canvas += p7

    canvas += Line(p4, p6)
    canvas += Line(p6, p5)
    canvas += Line(p5, p7)
    canvas += Line(p7, p4)
    canvas.make_polygon([p4, p5, p6, p7])

    canvas.make_intersection_points()
    print("Intersection Points:", len(canvas.inner_intersection_points))

    for i in range(0, WIDTH, 10):
        canvas.tk_canvas.create_line(i, 0, i, 5, fill="black")
        canvas.tk_canvas.create_line(i, 0, i, HEIGHT, fill="#C0C0C0")
        canvas.tk_canvas.create_text(i, 15, text=str(i), fill="black", anchor="nw", font=("Arial", 6), angle=90)
    for i in range(0, HEIGHT, 10):
        canvas.tk_canvas.create_line(0, i, 5, i, fill="black")
        canvas.tk_canvas.create_line(0, i, WIDTH, i, fill="#C0C0C0")
        canvas.tk_canvas.create_text(5, i, text=str(i), fill="black", anchor="nw", font=("Arial", 6), angle=0)

    for line in canvas.lines:
        p1, p2 = line
        canvas.tk_canvas.create_line(p1.x, p1.y, p2.x, p2.y, fill="red")

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if canvas.grid_matrix[y, x]:
                canvas.tk_canvas.create_rectangle(x - 1, y - 1, x + 1, y + 1, fill="black")

    inner_points = list[PointType]()
    polygon_center = Point(0, 0)

    for intersection in canvas.figure_intersections():
        polygon_center.x += intersection.x
        polygon_center.y += intersection.y
        inner_points.append(intersection)
        canvas.tk_canvas.create_oval(
            intersection.x - 3, intersection.y - 3,
            intersection.x + 3, intersection.y + 3,
            fill="blue"
        )
    
    polygon_center.x /= len(inner_points)
    polygon_center.y /= len(inner_points)

    if inner_points:
        sorted_points = sorted(
            inner_points,
            key=lambda p: np.arctan2(p.y - polygon_center.y, p.x - polygon_center.x),
        )

        for i in range(len(sorted_points)):
            a = sorted_points[i]
            b = sorted_points[(i + 1) % len(sorted_points)]
            canvas.tk_canvas.create_line(a.x, a.y, b.x, b.y, fill="green", dash=(2, 1), width=3)

            canvas.tk_canvas.create_line(
                polygon_center.x, polygon_center.y,
                a.x, a.y,
                fill="black", dash=(2, 4)
            )

    canvas.tk_canvas.create_oval(
        polygon_center.x - 3, polygon_center.y - 3,
        polygon_center.x + 3, polygon_center.y + 3,
        fill="green"
    )

    canvas.tk_canvas.mainloop()
