import unittest
from unittest.mock import patch, mock_open
from math import sqrt, isclose
from common.r3 import R3
from shadow.polyedr import Facet
from tests.matchers import R3ApproxMatcher, R3CollinearMatcher

from shadow.polyedr import Polyedr


class TestVoid(unittest.TestCase):

    # Эта грань не является вертикальной
    def test_vertical01(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        self.assertFalse(f.is_vertical())

    # Эта грань вертикальна
    def test_vertical02(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(0.0, 0.0, 1.0), R3(1.0, 0.0, 0.0)])
        self.assertTrue(f.is_vertical())

    # Нормаль к этой грани направлена вертикально вверх
    def test_h_normal01(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        self.assertEqual(R3CollinearMatcher(f.h_normal()), R3(0.0, 0.0, 1.0))

    # Нормаль к этой грани тоже направлена вертикально вверх
    def test_h_normal02(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(0.0, 3.0, 0.0), R3(3.0, 0.0, 0.0)])
        self.assertEqual(R3CollinearMatcher(f.h_normal()), R3(0.0, 0.0, 1.0))

    # Для нахождения нормали к этой грани рекомендуется нарисовать картинку
    def test_h_normal03(self):
        f = Facet([R3(1.0, 0.0, 0.0), R3(0.0, 1.0, 0.0), R3(0.0, 0.0, 1.0)])
        self.assertEqual(R3CollinearMatcher(f.h_normal()), R3(1.0, 1.0, 1.0))

    # Для каждой из следующих граней сначала «вручную» находятся
    # внешние нормали к вертикальным плоскостям, проходящим через
    # рёбра заданной грани, а затем проверяется, что эти нормали
    # имеют то же направление, что и вычисляемые методом v_normals

    # Нормали для треугольной грани
    def test_v_normal01(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        normals = [R3(-1.0, 0.0, 0.0), R3(0.0, -1.0, 0.0), R3(1.0, 1.0, 0.0)]
        for t in zip(f.v_normals(), normals):
            self.assertEqual(R3CollinearMatcher(t[0]), t[1])

    # Нормали для квадратной грани
    def test_v_normal02(self):
        f = Facet([
            R3(0.0, 0.0, 0.0),
            R3(2.0, 0.0, 0.0),
            R3(2.0, 2.0, 0.0),
            R3(0.0, 2.0, 0.0)
        ])
        normals = [
            R3(-1.0, 0.0, 0.0),
            R3(0.0, -1.0, 0.0),
            R3(1.0, 0.0, 0.0),
            R3(0.0, 1.0, 0.0)
        ]
        for t in zip(f.v_normals(), normals):
            self.assertEqual(R3CollinearMatcher(t[0]), t[1])

    # Нормали для ещё одной треугольной грани
    def test_v_normal03(self):
        f = Facet([R3(1.0, 0.0, 0.0), R3(0.0, 1.0, 0.0), R3(0.0, 0.0, 1.0)])
        normals = [R3(0.0, -1.0, 0.0), R3(1.0, 1.0, 0.0), R3(-1.0, 0.0, 0.0)]
        for t in zip(f.v_normals(), normals):
            self.assertEqual(R3CollinearMatcher(t[0]), t[1])

    # Центр квадрата
    def test_center01(self):
        f = Facet([
            R3(0.0, 0.0, 0.0),
            R3(2.0, 0.0, 0.0),
            R3(2.0, 2.0, 0.0),
            R3(0.0, 2.0, 0.0)
        ])
        self.assertEqual(R3ApproxMatcher(f.center()), (R3(1.0, 1.0, 0.0)))

    # Центр треугольника
    def test_center02(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        self.assertEqual(R3ApproxMatcher(f.center()), (R3(1.0, 1.0, 0.0)))

    def test_perimeter_project01(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        self.assertAlmostEqual(f.perimeter_project(), 6. + sqrt(18.))

    def test_perimeter_project02(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(0.0, 0.0, 1.0), R3(1.0, 0.0, 0.0)])
        self.assertAlmostEqual(f.perimeter_project(), 2.)

    def test_perimeter_project03(self):
        f = Facet([
            R3(0.0, 0.0, 0.0),
            R3(2.0, 0.0, 0.0),
            R3(2.0, 2.0, 0.0),
            R3(0.0, 2.0, 0.0)
        ])
        self.assertAlmostEqual(f.perimeter_project(), 8.)

    def test_perimeter_project04(self):
        f = Facet([R3(0.0, 0.0, -1.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        self.assertAlmostEqual(f.perimeter_project(), 6. + sqrt(18.))

    def test_perimeter_project05(self):
        f = Facet(
            [R3(1.0, -1.0, 13.0),
             R3(6.0, -1.0, -17.0),
             R3(5.0, 3.0, 8.0)])
        self.assertAlmostEqual(f.perimeter_project(),
                               5. + sqrt(17.) + sqrt(32.))

    def test_appropriate_center01(self):
        f = Facet([
            R3(0.0, 0.0, 0.0),
            R3(2.0, 0.0, 0.0),
            R3(2.0, 2.0, 0.0),
            R3(0.0, 2.0, 0.0)
        ])
        self.assertFalse(f.appropriate_center())

    def test_appropriate_center02(self):
        f = Facet([
            R3(0.0, 0.0, 0.0),
            R3(3.0, 0.0, 0.0),
            R3(3.0, 3.0, 0.0),
            R3(0.0, 3.0, 0.0)
        ])
        self.assertTrue(f.appropriate_center())

    def test_appropriate_center03(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(3.0, 0.0, 0.0), R3(0.0, 3.0, 0.0)])
        self.assertFalse(f.appropriate_center())

    def test_appropriate_center04(self):
        f = Facet([R3(0.0, 0.0, 0.0), R3(2.0, 0.0, 0.0), R3(0.0, 2.0, 0.0)])
        self.assertFalse(f.appropriate_center())

    def test_appropriate_center05(self):
        f = Facet([R3(0.5, 0.5, 0.0), R3(4.0, 0.0, 0.0), R3(0.0, 4.0, 0.0)])
        self.assertTrue(f.appropriate_center())

    def test_edge_vis_class01(self):
        f = Facet([R3(1.0, 0.0, 0.0), R3(0.0, 1.0, 0.0), R3(0.0, 0.0, 1.0)])
        with self.assertRaises(RuntimeError):
            f.edge_vis_class(None)

    def test_edge_vis_class02(self):
        fake_file_content = """200.0	45.0	45.0	30.0
8	4	16
-0.5	-0.5	0.5
-0.5	0.5	0.5
0.5	0.5	0.5
0.5	-0.5	0.5
-0.5	-0.5	-0.5
-0.5	0.5	-0.5
0.5	0.5	-0.5
0.5	-0.5	-0.5
4	5    6    2    1
4	3    2    6    7
4	3    7    8    4
4	1    4    8    5
"""
        fake_file_path = 'data/holey_box.geom'
        with patch('shadow.polyedr.open'.format(__name__),
                   new=mock_open(read_data=fake_file_content)) as _file:
            polyedr = Polyedr(fake_file_path)
            _file.assert_called_once_with(fake_file_path)

        for e in polyedr.edges:
            for f in polyedr.facets:
                e.shadow(f)

        self.assertEqual(polyedr.facets[0].edge_vis_class(polyedr), Facet.VIS)
        self.assertEqual(polyedr.facets[1].edge_vis_class(polyedr), Facet.VIS)
        self.assertEqual(polyedr.facets[2].edge_vis_class(polyedr),
                         Facet.PARVIS)
        self.assertEqual(polyedr.facets[3].edge_vis_class(polyedr),
                         Facet.PARVIS)

    def test_edge_vis_class03(self):
        fake_file_content = """150.0	45.0	45.0	30.0
8	2	8
2.0	2.0	0.5
2.0	-2.0	0.5
-2.0	-2.0	0.5
-2.0	2.0	0.5
-0.5	-0.5	-0.5
-0.5	0.5	-0.5
0.5	0.5	-0.5
0.5	-0.5	-0.5
4	1    2    3    4
4	5    6    7    8
"""
        fake_file_path = 'data/holey_box.geom'
        with patch('shadow.polyedr.open'.format(__name__),
                   new=mock_open(read_data=fake_file_content)) as _file:
            polyedr = Polyedr(fake_file_path)
            _file.assert_called_once_with(fake_file_path)

        for e in polyedr.edges:
            for f in polyedr.facets:
                e.shadow(f)

        self.assertEqual(polyedr.facets[0].edge_vis_class(polyedr), Facet.VIS)
        self.assertEqual(polyedr.facets[1].edge_vis_class(polyedr),
                         Facet.INVIS)
