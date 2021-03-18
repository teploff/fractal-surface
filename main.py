from ursina import Ursina, camera, window, Light, color, scene, Entity, held_keys, time, Mesh, Vec3, EditorCamera
from ursina.light import DirectionalLight
from ursina.scripts.generate_normals import generate_normals
from numba import jit
import math
import numpy
from scipy.spatial import Delaunay
from typing import List, Tuple


class Game(Ursina):
    def __init__(self):
        super().__init__()
        window.color = color.black
        window.fullscreen_size = 1920, 1080
        window.fullscreen = False

        Light(type='ambient', color=(0.5, 0.5, 0.5, 1))
        Light(type='directional', color=(0.5, 0.5, 0.5, 1), direction=(1, 1, 1))

        p1 = Point(0.0, 0.0, 0.0)
        p2 = Point(0.5, math.sqrt(3) / 2.0, 0.0)
        p3 = Point(1.0, 0.0, 0.0)
        h = math.sqrt(2.0/3.0)

        a, b, c, n = make_coef_surface(p1, p2, p3)
        p5, p6 = median_case(p1, p2, p3)

        p7 = find_p7_point(p1, p2, p5, p6)

        p4 = find_p4_point(a, b, c, n, h, p7)

        # count = 100
        # a1 = generate_point(ss.triangles[0].min_x, ss.triangles[0].max_x, ss.triangles[0].min_y, ss.triangles[0].max_y,
        #                     count, ((-3.0, 3.0), (-3.0, -3.0), (3.0, -3.0), (3.0, 3.0)))

        vertiti = [[p1.x, p1.y, p1.z], [p2.x, p2.y, p2.z], [p3.x, p3.y, p3.z], [p4.x, p4.y, p4.z]]
        trititi = [[0, 1, 2, 0], [0, 1, 3, 0], [0, 2, 3, 0], [1, 2, 3, 1]]
        # tri = Delaunay(a1)
        #
        # a1 = numpy.concatenate((a1, numpy.array([[numpy.random.uniform(-1, 1, size=(1, 1))[0][0]] for _ in range(len(a1))])), axis=1)
        # vertices = a1.tolist()
        #
        # triangles = tri.simplices.tolist()
        #
        # normals = generate_normals(vertices, triangles=triangles).tolist()
        normalstiti = generate_normals(vertiti, triangles=trititi).tolist()

        # self.surface = Entity(
        #     model=Mesh(vertices=vertices, triangles=triangles, normals=normals, colors=colors, thickness=3),
        #     scale=2)
        # self.surface.model.colorize(smooth=False)

        self.surface = Entity(
            model=Mesh(vertices=vertiti, triangles=trititi, mode='line', thickness=3), scale=2, color=color.magenta)

        mp1 = calc_midpoint(p1, p2)
        mp2 = calc_midpoint(p2, p3)
        mp3 = calc_midpoint(p3, p1)
        h_new = h * calc_distance(mp1, mp2) / calc_distance(p1, p2)
        cal_tetrahedron(mp1, mp2, mp3, h_new, self.surface)

        mp1 = calc_midpoint(p1, p2)
        mp2 = calc_midpoint(p2, p4)
        mp3 = calc_midpoint(p4, p1)
        h_new = h * calc_distance(mp1, mp2) / calc_distance(p1, p2)
        cal_tetrahedron(mp1, mp2, mp3, h_new, self.surface)

        mp1 = calc_midpoint(p2, p3)
        mp2 = calc_midpoint(p3, p4)
        mp3 = calc_midpoint(p4, p2)
        h_new = h * calc_distance(mp1, mp2) / calc_distance(p1, p2)
        cal_tetrahedron(mp1, mp2, mp3, h_new, self.surface)

        mp1 = calc_midpoint(p1, p3)
        mp2 = calc_midpoint(p3, p4)
        mp3 = calc_midpoint(p4, p1)
        h_new = h * calc_distance(mp1, mp2) / calc_distance(p1, p2)
        cal_tetrahedron(mp1, mp2, mp3, h_new, self.surface)

        EditorCamera()

    @staticmethod
    def new_game():
        scene.clear()

    def update(self):
        self.surface.rotation_y += held_keys['e'] * time.dt * 10
        self.surface.rotation_y -= held_keys['q'] * time.dt * 10

        self.surface.x += held_keys['d'] * time.dt * 5
        self.surface.x -= held_keys['a'] * time.dt * 5
        self.surface.y += held_keys['w'] * time.dt * 5
        self.surface.y -= held_keys['s'] * time.dt * 5

        self.surface.model.generate()

    def input(self, key):
        super().input(key)

    def get_midpoint(self):
        pass


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class Line:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def midpoint(self):
        return Point((self.p1.x + self.p2.x) / 2.0, (self.p1.y + self.p2.y) / 2.0, (self.p1.z + self.p2.z) / 2.0)


class Triangle:
    def __init__(self, line1: Line, line2: Line, line3: Line):
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3

    @property
    def min_x(self):
        return min(self.line1.p1.x, self.line1.p2.x, self.line2.p1.x, self.line2.p2.x, self.line3.p1.x, self.line3.p2.x)

    @property
    def max_x(self):
        return max(self.line1.p1.x, self.line1.p2.x, self.line2.p1.x, self.line2.p2.x, self.line3.p1.x, self.line3.p2.x)

    @property
    def min_y(self):
        return min(self.line1.p1.y, self.line1.p2.y, self.line2.p1.y, self.line2.p2.y, self.line3.p1.y, self.line3.p2.y)

    @property
    def max_y(self):
        return max(self.line1.p1.y, self.line1.p2.y, self.line2.p1.y, self.line2.p2.y, self.line3.p1.y, self.line3.p2.y)

    @property
    def min_z(self):
        return min(self.line1.p1.z, self.line1.p2.z, self.line2.p1.z, self.line2.p2.z, self.line3.p1.z, self.line3.p2.z)

    @property
    def max_z(self):
        return max(self.line1.p1.z, self.line1.p2.z, self.line2.p1.z, self.line2.p2.z, self.line3.p1.z, self.line3.p2.z)


class Surface:
    def __init__(self, triangles):
        self.triangles = triangles

    def get_ursina_samples(self) -> (tuple, tuple, tuple):
        vertices = []
        triangles = []

        for i, triangle in enumerate(self.triangles):
            triangles.append((i * 2 + i, i * 2 + i + 1, i * 2 + i + 2, i * 2 + i))
            vertices.append((triangle.line1.p1.x, triangle.line1.p1.y, triangle.line1.p1.z))
            vertices.append((triangle.line2.p1.x, triangle.line2.p1.y, triangle.line2.p1.z))
            vertices.append((triangle.line3.p1.x, triangle.line3.p1.y, triangle.line3.p1.z))

        return vertices, triangles, generate_normals(vertices, triangles=triangles).tolist()

    def fraction(self):
        new_triangles = []

        for triangle in self.triangles:
            p1 = triangle.line1.midpoint()
            p2 = triangle.line2.midpoint()
            p3 = triangle.line3.midpoint()

            new_triangles.append(Triangle(
                Line(Point(triangle.line1.p1.x, triangle.line1.p1.y, triangle.line1.p1.z), Point(p1.x, p1.y, p1.z)),
                Line(Point(p1.x, p1.y, p1.z), Point(p3.x, p3.y, p3.z)),
                Line(Point(p3.x, p3.y, p3.z), Point(triangle.line1.p1.x, triangle.line1.p1.y, triangle.line1.p1.z)),
            ))
            new_triangles.append(Triangle(
                Line(Point(p1.x, p1.y, p1.z), Point(triangle.line2.p1.x, triangle.line2.p1.y, triangle.line2.p1.z)),
                Line(Point(triangle.line2.p1.x, triangle.line2.p1.y, triangle.line2.p1.z), Point(p2.x, p2.y, p2.z)),
                Line(Point(p2.x, p2.y, p2.z), Point(p1.x, p1.y, p1.z)),
            ))
            new_triangles.append(Triangle(
                Line(Point(p2.x, p2.y, p2.z), Point(triangle.line3.p1.x, triangle.line3.p1.y, triangle.line3.p1.z)),
                Line(Point(triangle.line3.p1.x, triangle.line3.p1.y, triangle.line3.p1.z), Point(p3.x, p3.y, p3.z)),
                Line(Point(p3.x, p3.y, p3.z), Point(p2.x, p2.y, p2.z)),
            ))
            new_triangles.append(Triangle(
                Line(Point(p3.x, p3.y, p3.z), Point(p1.x, p1.y, p1.z)),
                Line(Point(p1.x, p1.y, p1.z), Point(p2.x, p2.y, p2.z)),
                Line(Point(p2.x, p2.y, p2.z), Point(p3.x, p3.y, p3.z)),
            ))

        self.triangles = new_triangles


def make_coef_surface(p1: Point, p2: Point, p3: Point) -> (float, float, float, float):
    """
    Вычисление коэффициентов плоскости A, B, C, проходящую через три точки p1, p2 и p3, и вектора нормали N к этой
    плоскости.
    :param p1: Первая точка
    :param p2: Вторая точка
    :param p3: Третья точка
    :return: Кожфиициенты клоскости A, B и C и проходящий через нее вектор нормали N
    """

    a = (p2.y - p1.y) * (p3.z - p1.z) - (p3.y - p1.y) * (p2.z - p1.z)
    b = (p3.x - p1.x) * (p2.z - p1.z) - (p2.x - p1.x) * (p3.z - p1.z)
    c = (p2.x - p1.x) * (p3.y - p1.y) - (p3.x - p1.x) * (p2.y - p1.y)
    n = math.sqrt(math.pow(a, 2) + math.pow(b, 2) + math.pow(c, 2))

    return a, b, c, n


def median_case(p1: Point, p2: Point, p3: Point) -> (Point, Point):
    """

    :param p1:
    :param p2:
    :param p3:
    :return:
    """

    p5 = Point((p2.x + p3.x) / 2.0, (p2.y + p3.y) / 2.0, (p2.z + p3.z) / 2.0)
    p6 = Point((p1.x + p3.x) / 2.0, (p1.y + p3.y) / 2.0, (p1.z + p3.z) / 2.0)

    return p5, p6


def find_p7_point(p1: Point, p2: Point, p5: Point, p6: Point) -> Point:
    """

    :param p1:
    :param p2:
    :param p5:
    :param p6:
    :return:
    """
    y = ((p5.y - p1.y) * (p6.y - p2.y) * p2.x - p6.x * p2.y * p5.y + p6.x * p2.y * p1.y + p2.x * p2.y * p5.y
         - p2.x * p2.y * p1.y + p5.x * p1.y * p6.y - p5.x * p1.y * p2.y - p1.x * p1.y * p6.y + p1.x * p1.y * p2.y
         - (p5.y - p1.y) * (p6.y - p2.y) * p1.x) / (p5.x * p6.y - p5.x * p2.y - p1.x * p6.y + p1.x * p2.y - p6.x * p5.y
                                                    + p6.x * p1.y + p2.x * p5.y - p2.x * p1.y)

    x = ((p5.x - p1.x) * (y - p1.y)) / (p5.y - p1.y) + p1.x

    # todo: bug: float division by zero
    z = ((x - p1.x) * (p5.z - p1.z)) / (p5.x - p1.x) + p1.z

    return Point(x, y, z)


def find_p4_point(a: float, b: float, c: float, n: float, h: float, p7: Point) -> Point:
    """

    :param a:
    :param b:
    :param c:
    :param n:
    :param h:
    :param p7:
    :return:
    """

    x = p7.x + (a * h) / n
    y = p7.y + (b * h) / n
    z = p7.z + (c * h) / n

    return Point(x, y, z)


def calc_midpoint(p1: Point, p2: Point) -> Point:
    """

    :param p1:
    :param p2:
    :return:
    """

    return Point((p1.x + p2.x) / 2.0, (p1.y + p2.y) / 2.0, (p1.z + p2.z) / 2.0)


def calc_distance(p1: Point, p2: Point) -> float:
    """

    :param p1:
    :param p2:
    :return:
    """

    return math.sqrt(math.pow(p2.x - p1.x, 2) + math.pow(p2.y - p1.y, 2) + math.pow(p2.z - p1.z, 2))


def cal_tetrahedron(p1: Point, p2: Point, p3: Point, h: float, parent: Entity) -> None:
    """

    :param p1:
    :param p2:
    :param p3:
    :param h:
    :param parent:
    :return:
    """

    a, b, c, n = make_coef_surface(p1, p2, p3)
    p5, p6 = median_case(p1, p2, p3)

    p7 = find_p7_point(p1, p2, p5, p6)

    p4 = find_p4_point(a, b, c, n, h, p7)

    # count = 100
    # a1 = generate_point(ss.triangles[0].min_x, ss.triangles[0].max_x, ss.triangles[0].min_y, ss.triangles[0].max_y,
    #                     count, ((-3.0, 3.0), (-3.0, -3.0), (3.0, -3.0), (3.0, 3.0)))

    vertiti = [[p1.x, p1.y, p1.z], [p2.x, p2.y, p2.z], [p3.x, p3.y, p3.z], [p4.x, p4.y, p4.z]]
    trititi = [[0, 1, 2, 0], [0, 1, 3, 0], [0, 2, 3, 0], [1, 2, 3, 1]]
    # tri = Delaunay(a1)
    #
    # a1 = numpy.concatenate((a1, numpy.array([[numpy.random.uniform(-1, 1, size=(1, 1))[0][0]] for _ in range(len(a1))])), axis=1)
    # vertices = a1.tolist()
    #
    # triangles = tri.simplices.tolist()
    #
    # normals = generate_normals(vertices, triangles=triangles).tolist()
    # normalstiti = generate_normals(vertiti, triangles=trititi).tolist()

    # self.surface = Entity(
    #     model=Mesh(vertices=vertices, triangles=triangles, normals=normals, colors=colors, thickness=3),
    #     scale=2)
    # self.surface.model.colorize(smooth=False)

    tetrahedron = Entity(parent=parent, model=Mesh(vertices=vertiti, triangles=trititi, mode='line', thickness=5), color=color.magenta)


def generate_point(x_min, x_max, y_min, y_max, count, polygon):
    """

    :param x_min:
    :param x_max:
    :param y_min:
    :param y_max:
    :param count:
    :param polygon:
    :return:
    """
    i = 0
    result = [point for point in polygon]

    while i != count:
        x = numpy.random.uniform(x_min, x_max, size=(1, 1))[0][0]
        y = numpy.random.uniform(y_min, y_max, size=(1, 1))[0][0]

        if ray_tracing(x, y, polygon):
            result.append((x, y))
            i += 1

    return numpy.array(result)


@jit(nopython=True)
def ray_tracing(x, y, poly):
    n = len(poly)
    inside = False
    p2x = 0.0
    p2y = 0.0
    xints = 0.0
    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


if __name__ == '__main__':
    game = Game()
    update = game.update
    game.run()
