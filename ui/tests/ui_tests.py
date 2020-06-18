import unittest, sys, os, math

sys.path.append(os.getcwd())
from ui.ui import *
from physics.maths import *


class TestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = Game()

    def test_get_max_visible_angle(self):
        self.game.get_max_visible_angle()
        max_angle = self.game.max_vis_angle
        self.assertAlmostEqual(1.075076697, max_angle, 9)

    def test_get_plane_object_intersection(self):
        self.game.camera_position = [0.0, 0.0, 10.0]
        self.game.camera_start_ang = [-math.pi / 4, 0, 0]
        self.game.initialise_camera()

        line_1 = [[0.0, -10.0, 0.0], [0.0, 30.0, 0.0]]
        coords_to_point = []
        for point in line_1:
            coords_to_point.append([i - j for i, j in zip(point, self.game.camera_position)])
        angles = []

        for point in coords_to_point:
            angles.append(vector_ang(point, self.game.cp_normal, False))

        print(angles)
        self.assertAlmostEqual(math.pi / 2, angles[0], 10)
        self.assertAlmostEqual(0.4636476, angles[1], 7)
        points_visible = [False, True]

        print(coords_to_point)
        new_coords = self.game._get_plane_object_intersection(coords_to_point, points_visible, angles)
        
        print(new_coords)
        print(self.game.max_vis_angle)


if __name__ == '__main__':
    unittest.main()