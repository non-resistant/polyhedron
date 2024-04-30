from math import pi
from functools import reduce
from operator import add
from common.r3 import R3
from common.tk_drawer import TkDrawer


class Segment:
    """ Одномерный отрезок """

    # Параметры конструктора: начало и конец отрезка (числа)

    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin

    def __eq__(self, other):
        return self.beg == other.beg and self.fin == other.fin

    # Отрезок вырожден?
    def is_degenerate(self):
        return self.beg >= self.fin

    # Пересечение с отрезком
    def intersect(self, other):
        if other.beg > self.beg:
            self.beg = other.beg
        if other.fin < self.fin:
            self.fin = other.fin
        return self

    # Разность отрезков
    # Разность двух отрезков всегда является списком из двух отрезков!
    def subtraction(self, other):
        return [
            Segment(self.beg, self.fin if self.fin < other.beg else other.beg),
            Segment(self.beg if self.beg > other.fin else other.fin, self.fin)
        ]


class Edge:
    """ Ребро полиэдра """
    # Начало и конец стандартного одномерного отрезка
    SBEG, SFIN = 0.0, 1.0
    VIS = 2
    PARVIS = 1
    INVIS = 0

    # Параметры конструктора: начало и конец ребра (точки в R3)
    def __init__(self, beg, fin):
        self.beg, self.fin = beg, fin
        # Список «просветов»
        self.gaps = [Segment(Edge.SBEG, Edge.SFIN)]

    # Учёт тени от одной грани
    def shadow(self, facet):
        # «Вертикальная» грань не затеняет ничего
        if facet.is_vertical():
            return
        # Нахождение одномерной тени на ребре
        shade = Segment(Edge.SBEG, Edge.SFIN)
        for u, v in zip(facet.vertexes, facet.v_normals()):
            shade.intersect(self.intersect_edge_with_normal(u, v))
            if shade.is_degenerate():
                return

        shade.intersect(
            self.intersect_edge_with_normal(facet.vertexes[0],
                                            facet.h_normal()))
        if shade.is_degenerate():
            return

        # Преобразование списка «просветов», если тень невырождена
        gaps = [s.subtraction(shade) for s in self.gaps]
        self.gaps = [s for s in reduce(add, gaps, []) if not s.is_degenerate()]

    # Преобразование одномерных координат в трёхмерные
    def r3(self, t):
        return self.beg * (Edge.SFIN - t) + self.fin * t

    # Пересечение ребра с полупространством, задаваемым точкой (a)
    # на плоскости и вектором внешней нормали (n) к ней
    def intersect_edge_with_normal(self, a, n):
        f0, f1 = n.dot(self.beg - a), n.dot(self.fin - a)
        if f0 >= 0.0 and f1 >= 0.0:
            return Segment(Edge.SFIN, Edge.SBEG)
        if f0 < 0.0 and f1 < 0.0:
            return Segment(Edge.SBEG, Edge.SFIN)
        x = -f0 / (f1 - f0)
        return Segment(Edge.SBEG, x) if f0 < 0.0 else Segment(x, Edge.SFIN)

    def visibility_class(self):
        if len(self.gaps) == 0:
            return Edge.INVIS
        if len(self.gaps) == 1 and self.gaps[0] == Segment(
                Edge.SBEG, Edge.SFIN):
            return Edge.VIS
        return Edge.PARVIS


class Facet:
    """ Грань полиэдра """

    # Параметры конструктора: список вершин
    VIS = 2
    PARVIS = 1
    INVIS = 0

    def __init__(self, vertexes, edge_range=None):
        self.vertexes = vertexes
        self.edge_range = edge_range

    # «Вертикальна» ли грань?
    def is_vertical(self):
        return self.h_normal().dot(Polyedr.V) == 0.0

    # Нормаль к «горизонтальному» полупространству
    def h_normal(self):
        n = (self.vertexes[1] - self.vertexes[0]).cross(self.vertexes[2] -
                                                        self.vertexes[0])
        return n * (-1.0) if n.dot(Polyedr.V) < 0.0 else n

    # Нормали к «вертикальным» полупространствам, причём k-я из них
    # является нормалью к грани, которая содержит ребро, соединяющее
    # вершины с индексами k-1 и k
    def v_normals(self):
        return [self._vert(x) for x in range(len(self.vertexes))]

    # Вспомогательный метод
    def _vert(self, k):
        n = (self.vertexes[k] - self.vertexes[k - 1]).cross(Polyedr.V)
        return n * \
            (-1.0) if n.dot(self.vertexes[k - 1] - self.center()) < 0.0 else n

    # Центр грани
    def center(self):
        return (sum(self.vertexes, R3(0.0, 0.0, 0.0)) *
                (1.0 / len(self.vertexes)))

    # def original_center(self, polyedr):
    #     return (self.center() /
    #             self.scale).rz(-self.gamma).ry(-self.beta).rz(-self.alpha)

    def perimeter_project(self):
        s = 0
        for i in range(len(self.vertexes)):
            s += abs(
                R3(self.vertexes[i].x, self.vertexes[i].y, 0) -
                R3(self.vertexes[(i + 1) % len(self.vertexes)].x,
                   self.vertexes[(i + 1) % len(self.vertexes)].y, 0))
        return s

    def appropriate_center(self):
        return abs(self.center().x - 2.) < 1.

    def edge_vis_class(self, polyedr):
        if self.edge_range is None:
            raise RuntimeError("{self} does not contain it's edges' info.")
        if (polyedr.edges[self.edge_range[0]].visibility_class() == Edge.PARVIS
                or any(polyedr.edges[i - 1].visibility_class() !=
                       polyedr.edges[i].visibility_class()
                       for i in range(self.edge_range[0] +
                                      1, self.edge_range[1]))):
            return Facet.PARVIS
        if polyedr.edges[self.edge_range[0]].visibility_class() == Edge.VIS:
            return Facet.VIS
        return Facet.INVIS


class Polyedr:
    """ Полиэдр """
    # вектор проектирования
    V = R3(0.0, 0.0, 1.0)

    # Параметры конструктора: файл, задающий полиэдр
    def __init__(self, file):

        # списки вершин, рёбер и граней полиэдра
        self.vertexes, self.edges, self.facets = [], [], []

        # список строк файла
        with open(file) as f:
            for i, line in enumerate(f):
                if i == 0:
                    # обрабатываем первую строку; buf - вспомогательный массив
                    buf = line.split()
                    # коэффициент гомотетии
                    self.scale = float(buf.pop(0))
                    # углы Эйлера, определяющие вращение
                    self.alpha, self.beta, self.gamma = (float(x) * pi / 180.0
                                                         for x in buf)
                elif i == 1:
                    # во второй строке число вершин, граней и рёбер полиэдра
                    nv, nf, ne = (int(x) for x in line.split())
                elif i < nv + 2:
                    # задание всех вершин полиэдра
                    x, y, z = (float(x) for x in line.split())
                    self.vertexes.append(
                        R3(x, y, z).rz(self.alpha).ry(self.beta).rz(self.gamma)
                        * self.scale)
                else:
                    # вспомогательный массив
                    buf = line.split()
                    # количество вершин очередной грани
                    size = int(buf.pop(0))
                    # массив вершин этой грани
                    vertexes = list(self.vertexes[int(n) - 1] for n in buf)
                    # задание рёбер грани
                    edge_range = [len(self.edges)]
                    for n in range(size):
                        self.edges.append(Edge(vertexes[n - 1], vertexes[n]))
                    edge_range.append(len(self.edges))
                    # задание самой грани
                    self.facets.append(Facet(vertexes, edge_range))

    # Метод изображения полиэдра
    def draw(self, tk):  # pragma: no cover
        tk.clean()
        for e in self.edges:
            for f in self.facets:
                e.shadow(f)
            for s in e.gaps:
                tk.draw_line(e.r3(s.beg), e.r3(s.fin))

    def character(self):
        return sum(
            f.perimeter_project() for f in self.facets
            if f.appropriate_center() and f.edge_vis_class() == Facet.INVIS)
