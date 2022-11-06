import unittest, sys, os, math

sys.path.append(os.getcwd())
from ui.ui import *
from physics.maths import *


class TestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game = Game()

    # def test_get_max_visible_angle(self):
    #     self.game.get_max_visible_angle()
    #     max_angle = self.game.max_vis_angle
    #     self.assertAlmostEqual(1.075076697, max_angle, 9)

    # def test_get_plane_object_intersection(self):
    #     self.game.camera_position = [0.0, 0.0, 10.0]
    #     self.game.camera_start_ang = [-math.pi / 4, 0, 0]
    #     self.game.initialise_camera()

    #     line_1 = [[0.0, -10.0, 0.0], [0.0, 30.0, 0.0]]
    #     coords_to_point = []
    #     for point in line_1:
    #         coords_to_point.append([i - j for i, j in zip(point, self.game.camera_position)])
    #     angles = []

    #     for point in coords_to_point:
    #         angles.append(vector_ang(point, self.game.cp_normal, False))

    #     print(angles)
    #     self.assertAlmostEqual(math.pi / 2, angles[0], 10)
    #     self.assertAlmostEqual(0.4636476, angles[1], 7)
    #     points_visible = [False, True]

    #     print(coords_to_point)
    #     new_coords = self.game._get_plane_object_intersection(coords_to_point, points_visible, angles)

    #     print(new_coords)
    #     print(self.game.max_vis_angle)

    def test_get_perspective_intersection_plane_right_delta_x(self):
        print("\n", self._testMethodName)
        self.game.camera_position = [0.0, 0.0, 0.0]
        self.game.camera_start_ang = [0, 0, 0]
        self.game.initialise_camera()

        line_1 = [[-5, 10.0, 0.0], [11.0, 10.0, 0.0]]
        plane = self.game.get_perspective_intersection_plane(line_1[0], line_1[1])

        self.assertEqual(plane, self.game.cp_normal_right)

        # line_1 mirrored in z-axis
        line_2 = [[5, 10.0, 0.0], [-11.0, 10.0, 0.0]]
        plane = self.game.get_perspective_intersection_plane(line_2[0], line_2[1])

        self.assertEqual(plane, self.game.cp_normal_left)

    def test_get_perspective_intersection_plane_top_delta_z(self):
        print("\n", self._testMethodName)
        self.game.camera_position = [0.0, 0.0, 0.0]
        self.game.camera_start_ang = [0, 0, 0]
        self.game.initialise_camera()

        line_1 = [[0, 10.0, -2.5], [0, 10.0, 10.0]]
        plane = self.game.get_perspective_intersection_plane(line_1[0], line_1[1])

        self.assertEqual(plane, self.game.cp_normal_top)

        # line_1 mirrored in x-axis
        line_2 = [[0, 10.0, 2.5], [0, 10.0, -10.0]]
        plane = self.game.get_perspective_intersection_plane(line_2[0], line_2[1])

        self.assertEqual(plane, self.game.cp_normal_bottom)

    def test_get_perspective_intersection_plane_top_delta_xz_from_centre(self):
        print("\n", self._testMethodName)
        self.game.camera_position = [0.0, 0.0, 0.0]
        self.game.camera_start_ang = [0, 0, 0]
        self.game.initialise_camera()

        # Line angle = 45 degrees from x-axis
        # result top
        line_1 = [[0, 10.0, 0], [20, 10.0, 20]]
        plane = self.game.get_perspective_intersection_plane(line_1[0], line_1[1])

        self.assertEqual(plane, self.game.cp_normal_top)

        # line_1 mirrored in x-axis: result bottom
        # Line angle = -45 degrees from x-axis
        line_2 = [[0, 10.0, 0], [20, 10.0, -20]]
        plane = self.game.get_perspective_intersection_plane(line_2[0], line_2[1])

        self.assertEqual(plane, self.game.cp_normal_bottom)

        # line_1 mirrored in z-axis: result top
        # Line angle = -45 degrees from negative x-axis
        line_3 = [[0, 10.0, 0], [-20, 10.0, 20]]
        plane = self.game.get_perspective_intersection_plane(line_3[0], line_3[1])

        self.assertEqual(plane, self.game.cp_normal_top)

        # line_1 mirrored in x-axis & z-axis: result bottom
        # Line angle = 45 degrees from negative x-axis
        line_4 = [[0, 10.0, 0], [-20, 10.0, -20]]
        plane = self.game.get_perspective_intersection_plane(line_4[0], line_4[1])

        self.assertEqual(plane, self.game.cp_normal_bottom)

    def test_get_perspective_intersection_plane_top_delta_xz_from_centre_2(self):
        print("\n", self._testMethodName)
        self.game.camera_position = [0.0, 0.0, 0.0]
        self.game.camera_start_ang = [0, 0, 0]
        self.game.initialise_camera()

        # Line angle = 26.56 degrees from x-axis
        # result right
        line_1 = [[0, 10.0, 0], [20, 10.0, 10]]
        plane = self.game.get_perspective_intersection_plane(line_1[0], line_1[1])

        self.assertEqual(plane, self.game.cp_normal_right)

        # line_1 mirrored in x-axis: result right
        # Line angle = -26.56 degrees from x-axis
        line_2 = [[0, 10.0, 0], [20, 10.0, -10]]
        plane = self.game.get_perspective_intersection_plane(line_2[0], line_2[1])

        self.assertEqual(plane, self.game.cp_normal_right)

        # line_1 mirrored in x-axis: result left
        # Line angle = -26.56 degrees from negative x-axis
        line_3 = [[0, 10.0, 0], [-20, 10.0, 10]]
        plane = self.game.get_perspective_intersection_plane(line_3[0], line_3[1])

        self.assertEqual(plane, self.game.cp_normal_left)

        # line_1 mirrored in x-axis & z-axis: result left
        # Line angle = 26.56 degrees from negative x-axis
        line_4 = [[0, 10.0, 0], [-20, 10.0, -10]]
        plane = self.game.get_perspective_intersection_plane(line_4[0], line_4[1])

        self.assertEqual(plane, self.game.cp_normal_left)

    def test_get_perspective_intersection_plane_top_delta_xz_from_x_2_shift_from_centre(
        self,
    ):
        print("\n", self._testMethodName)
        self.game.camera_position = [0.0, 0.0, 0.0]
        self.game.camera_start_ang = [0, 0, 0]
        self.game.initialise_camera()

        # Line angle = 26.56 degrees from x-axis
        line_1 = [[2, 10.0, 0], [22, 10.0, 10]]
        plane = self.game.get_perspective_intersection_plane(line_1[0], line_1[1])
        self.assertEqual(plane, self.game.cp_normal_right)

        # Line angle = -26.56 degrees from x-axis
        line_2 = [[2, 10.0, 0], [22, 10.0, -10]]
        plane = self.game.get_perspective_intersection_plane(line_2[0], line_2[1])
        self.assertEqual(plane, self.game.cp_normal_right)

        # Line angle = -26.56 degrees from negative x-axis
        line_3 = [[2, 10.0, 0], [-18, 10.0, 10]]
        plane = self.game.get_perspective_intersection_plane(line_3[0], line_3[1])
        self.assertEqual(plane, self.game.cp_normal_left)

        # Line angle = 26.56 degrees from negative x-axis
        line_4 = [[2, 10.0, 0], [-18, 10.0, 10]]
        plane = self.game.get_perspective_intersection_plane(line_4[0], line_4[1])
        self.assertEqual(plane, self.game.cp_normal_left)


if __name__ == "__main__":
    unittest.main()
