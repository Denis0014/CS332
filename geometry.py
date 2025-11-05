import numpy as np
from typing import Union, Any

Shape = Union["PointType", "LineType"]
Number = Union[int, float]
PointType = Union["BasePoint", "Point"]
LineType = Union["BaseLine", "Line"]

class BasePoint:
    def __init__(self, x: Number, y: Number) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        features = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items())
        if features:
            return f"{self.__class__.__name__}({self.x}, {self.y}, {features})"
        return f"{self.__class__.__name__}({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BasePoint):
            return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)

    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __iter__(self):
        yield self.x
        yield self.y


class Point(BasePoint):
    def __init__(self, x: Number, y: Number) -> None:
        super().__init__(x, y)
        self.__features = dict[str, Any]()

    def __getitem__(self, item: str) -> Any:
        return self.__features.get(item, None)
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.__features[key] = value

    def __repr__(self) -> str:
        features = ", ".join(f"{k}={repr(v)}" for k, v in self.__features.items())
        if features:
            return f"{self.__class__.__name__}({self.x}, {self.y}, {features})"
        return f"{self.__class__.__name__}({self.x}, {self.y})"


class BaseLine:
    def __init__(self, start: PointType, end: PointType) -> None:
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.start}, {self.end})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseLine):
            return False
        return self.start == other.start and self.end == other.end

    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)

    def __hash__(self) -> int:
        return hash((self.start, self.end))
    
    def __iter__(self):
        yield self.start
        yield self.end


class Line(BaseLine):
    def __init__(self, start: PointType, end: PointType) -> None:
        super().__init__(start, end)
        self.__features = dict[str, Any]()

    def __getitem__(self, item: str) -> Any:
        return self.__features.get(item, None)
    
    def __setitem__(self, key: str, value: Any) -> None:
        self.__features[key] = value

    def __repr__(self) -> str:
        features = ", ".join(f"{k}={repr(v)}" for k, v in self.__features.items())
        if features:
            return f"{self.__class__.__name__}({self.start}, {self.end}, {features})"
        return f"{self.__class__.__name__}({self.start}, {self.end})"


class BaseCanvas:
    def __init__(self, width: int, height: int) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive values, got " + str(width) + " and " + str(height))
        
        self.width = width
        self.height = height
        self.grid_matrix: np.ndarray = np.zeros((height, width), dtype=bool)
        self.points: list[PointType] = []
        self.lines: list[LineType] = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.width}, {self.height}, points_count={len(self.points)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseCanvas):
            return False
        return (
            self.width == other.width
            and self.height == other.height
            and self.grid_matrix == other.grid_matrix
        )

    def __ne__(self, value: object) -> bool:
        return not self.__eq__(value)

    def __add__(self, shape: Shape) -> "BaseCanvas":
        if isinstance(shape, BasePoint):
            if 0 <= shape.x < self.width - 1 and 0 <= shape.y < self.height - 1:
                self.grid_matrix[int(shape.y), int(shape.x)] = True
            self.points.append(shape)

            return self

        else:
            self.lines.append(shape)

        return self

    def __sub__(self, point: PointType) -> "BaseCanvas":
        if not (0 <= point.x < self.width - 1 and 0 <= point.y < self.height - 1):
            raise ValueError("Point coordinates must be within the canvas dimensions, got " + str(point.x) + ", " + str(point.y))

        self.grid_matrix[int(point.y), int(point.x)] = False
        self.points.remove(point)
        return self

    def __contains__(self, point: PointType) -> bool:
        if not (0 <= point.x < self.width - 1 and 0 <= point.y < self.height - 1):
            return False

        return self.grid_matrix[int(point.y), int(point.x)]

    def __next__(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid_matrix[y, x]:
                    return Point(x, y)
        raise StopIteration

    def __iter__(self):
        return self

    def clear(self) -> None:
        self.grid_matrix = np.zeros((self.height, self.width), dtype=bool)
        self.points.clear()

    def transform(self, matrix: np.ndarray) -> None:
        self.old_point = None

        new_grid_matrix: np.ndarray = np.zeros((self.height, self.width), dtype=bool)
        new_points: list[PointType] = []

        for x, y in self.points:
            vec = np.array([x, y, 1])
            x_new, y_new, _ = matrix @ vec
            x_new, y_new = int(round(x_new)), int(round(y_new))
            if 0 <= x_new < self.width and 0 <= y_new < self.height:
                new_grid_matrix[y_new, x_new] = True
                new_points.append(Point(x_new, y_new))

        self.points = new_points
