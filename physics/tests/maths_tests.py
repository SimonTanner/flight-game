import unittest, sys, os, math

sys.path.append(os.getcwd())
from physics.maths import *


class TestEQNS(unittest.TestCase):
    def test_get_line_equations_in_xy_plane(self):
        point_1 = (10.0, 10.0, 0.0)
        point_2 = (0.0, 0.0, 0.0)

        eqns = get_line_equations(point_1, point_2)

        self.assertEqual(eqns["y_x"], {"coeff": 1.0, "const": 0.0})
        self.assertEqual(eqns["z_y"], {"coeff": 0.0, "const": 0.0})
        self.assertEqual(eqns["x_z"], {"coeff": None, "const": 0.0})

    def test_get_line_equations_in_x_axis(self):
        point_1 = (10.0, 10.0, 0.0)
        point_2 = (10.0, 0.0, 0.0)

        eqns = get_line_equations(point_1, point_2)

        self.assertEqual(eqns["y_x"], {"coeff": None, "const": 10.0})
        self.assertEqual(eqns["z_y"], {"coeff": 0.0, "const": 0.0})
        self.assertEqual(eqns["x_z"], {"coeff": None, "const": 0.0})

    def test_get_line_equations_in_xyz_plane(self):
        point_1 = (10.0, 10.0, 0.0)
        point_2 = (10.0, 0.0, 10.0)

        eqns = get_line_equations(point_1, point_2)

        self.assertEqual(eqns["y_x"], {"coeff": None, "const": 10.0})
        self.assertEqual(eqns["z_y"], {"coeff": -1.0, "const": 10.0})
        self.assertEqual(eqns["x_z"], {"coeff": 0.0, "const": 10.0})

        point_1 = (10.0, 10.0, 0.0)
        point_2 = (5.0, 0.0, 10.0)

        eqns = get_line_equations(point_1, point_2)

        self.assertEqual(eqns["y_x"], {"coeff": 2.0, "const": -10.0})
        self.assertEqual(eqns["z_y"], {"coeff": -1.0, "const": 10.0})
        self.assertEqual(eqns["x_z"], {"coeff": -0.5, "const": 10.0})

    def test_get_plane_x_plane(self):
        normal = [0.0, 1.0, 0.0]
        expected_plane = {"D": 1.0, "x": 0.0, "y": 1.0, "z": 0.0}

        point_1 = (10.0, 10.0, 0.0)
        point_2 = (10.0, 0.0, 10.0)

        plane_eqn = get_plane(normal, normal)
        self.assertEqual(expected_plane, plane_eqn)

        point_in_plane = (0.0, 1.0, 1.0)

        plane_eqn = get_plane(normal, point_in_plane)
        self.assertEqual(expected_plane, plane_eqn)

    def test_get_plane_xy_plane(self):
        plane_vector = [1.0, 1.0, 0.0]
        normal = normalise_vector(plane_vector)
        sqrt_2 = math.sqrt(2)

        assert normal[0] == 1 / sqrt_2
        assert normal[1] == 1 / sqrt_2
        assert normal[2] == 0.0

        expected_plane = {"D": sqrt_2, "x": 1 / sqrt_2, "y": 1 / sqrt_2, "z": 0.0}

        plane_eqn = get_plane(normal, plane_vector)

        for key, exp_value in expected_plane.items():
            self.assertAlmostEqual(exp_value, plane_eqn[key])

        # Check using a 2nd point in the plane
        point_in_plane = (0.0, 2.0, 1.0)

        plane_eqn = get_plane(normal, point_in_plane)

        for key, exp_value in expected_plane.items():
            self.assertAlmostEqual(exp_value, plane_eqn[key])

    def test_plane_line_interesect_delta_xyz(self):
        normal = [0.0, 1.0, 0.0]
        plane = get_plane(normal, normal)
        point_1 = (0.0, 0.0, 0.0)
        point_2 = (8.0, 10000001.0, -6.0)

        eqns = get_line_equations(point_1, point_2)

        intersect_point = plane_line_interesect(plane, eqns)

        expected_total, total = check_coords_in_plane(plane, intersect_point)

        self.assertEqual(expected_total, total)

    def test_plane_line_interesect_delta_y(self):
        # test for vector parallel to an axis
        perp_vector_to_plane = [-1.0, 1.0, 0.0]
        normal = normalise_vector(perp_vector_to_plane)

        plane = get_plane(normal, perp_vector_to_plane)
        point_1 = (8.0, 1.0, -6.0)
        point_2 = (8.0, 10000001.0, -6.0)

        eqns = get_line_equations(point_1, point_2)

        intersect_point = plane_line_interesect(plane, eqns)

        expected_total, total = check_coords_in_plane(plane, intersect_point)

        self.assertEqual(expected_total, total)

    def test_plane_line_interesect_delta_yz(self):
        # test for vector parallel to an axis
        perp_vector_to_plane = [-1.0, 1.0, 0.0]
        normal = normalise_vector(perp_vector_to_plane)

        # test when only no change in one axis
        plane = get_plane(normal, perp_vector_to_plane)
        point_1 = (8.0, 1.0, -0.0)
        point_2 = (8.0, 10000001.0, -60.0)

        eqns = get_line_equations(point_1, point_2)

        intersect_point = plane_line_interesect(plane, eqns)

        expected_total, total = check_coords_in_plane(plane, intersect_point)

        self.assertEqual(expected_total, total)

    def test_plane_line_interesect_delta_yz(self):
        # test for vector parallel to an axis
        perp_vector_to_plane = [-1.0, 1.0, 0.0]
        normal = normalise_vector(perp_vector_to_plane)

        # test when only no change in one axis
        plane = get_plane(normal, perp_vector_to_plane)
        point_1 = (20.0, 1.0, -0.0)
        point_2 = (8.0, 10000001.0, -60.0)

        eqns = get_line_equations(point_1, point_2)

        intersect_point = plane_line_interesect(plane, eqns)

        expected_total, total = check_coords_in_plane(plane, intersect_point)

        self.assertAlmostEqual(expected_total, total)

    # def test_plane_line_interesect_delta_z(self):
    #     # test for vector parallel to an axis
    #     perp_vector_to_plane = [0.9685831611286307, -0.24868988716485613, 0.0]
    #     normal = normalise_vector(perp_vector_to_plane)

    #     # test when only no change in one axis
    #     plane = get_plane(normal, perp_vector_to_plane)
    #     point_1 = (9.450127700171018, 9.97583431643897, -2.5)
    #     point_2 = (9.450127700171018, 9.97583431643897, 3.5)

    #     eqns = get_line_equations(point_1, point_2)

    #     intersect_point = plane_line_interesect(plane, eqns)

    #     expected_total, total = check_coords_in_plane(plane, intersect_point)

    #     self.assertAlmostEqual(expected_total, total)


class TestConePlaneBothPointsOutOfCone(unittest.TestCase):
    @staticmethod
    def check_is_on_cone(angle, point):
        """
        Should return 0.0 if a point lies on the cone, angle is the angle between the cone central axis
        and the surface
        """
        tan_ang = math.tan(angle)
        point = [p**2 for p in point]
        return point[1] * tan_ang**2 - point[0] - point[2]

    def test_cone_plane_get_simple_line_intersect_points(self):

        angle = math.pi / 4
        cone_plane = ConePlane(angle)
        self.assertEqual(cone_plane.cone_angle, angle)

        line_coords = [[-3.0, 1.0, 0.0], [3.0, 1.0, 0.0]]
        angles = [0.0, 0.0, 0.0]

        intersect_point = cone_plane.plane_line_interesect(line_coords, angles)
        for point in intersect_point:
            # Extra check that point lies on cone
            check_val = self.check_is_on_cone(angle, point)
            self.assertAlmostEqual(check_val, 0)

        expected_point = [[-1.0, 1.0, 0.0], [1.0, 1.0, 0.0]]

        for i in range(len(intersect_point)):
            for j in range(len(intersect_point[i])):
                self.assertAlmostEqual(intersect_point[i][j], expected_point[i][j], 5)

    def test_cone_plane_get_line_angled_in_xy_plane_intersect_points(self):

        angle = math.pi / 4
        cone_plane = ConePlane(angle)
        self.assertEqual(cone_plane.cone_angle, angle)

        line_coords = [[-3.0, 1.0, 0.0], [3.0, 0.5, 0.0]]
        angles = [0.0, 0.0, 0.0]

        intersect_point = cone_plane.plane_line_interesect(line_coords, angles)
        for point in intersect_point:
            # Extra check that point lies on cone
            check_val = self.check_is_on_cone(angle, point)
            self.assertAlmostEqual(check_val, 0)

        expected_point = [
            [-0.8181818181818181, 0.8181818181818182, 0.0],
            [0.6923076923076924, 0.6923076923076924, 0.0],
        ]

        for i in range(len(intersect_point)):
            for j in range(len(intersect_point[i])):
                self.assertAlmostEqual(intersect_point[i][j], expected_point[i][j], 5)

        line_coords = [[-3.0, 1.0, 0.0], [3.0, 2.0, 0.0]]
        angles = [0.0, 0.0, 0.0]

        intersect_point = cone_plane.plane_line_interesect(line_coords, angles)
        for point in intersect_point:
            # Extra check that point lies on cone
            check_val = self.check_is_on_cone(angle, point)
            self.assertAlmostEqual(check_val, 0)

        expected_point = [
            [-1.2857142857142856, 1.2857142857142856, 0.0],
            [1.7999999999999998, 1.7999999999999998, 0.0],
        ]

        for i in range(len(intersect_point)):
            for j in range(len(intersect_point[i])):
                self.assertAlmostEqual(intersect_point[i][j], expected_point[i][j], 5)

    def test_cone_plane_get_line_angled_in_xz_plane_intersect_points(self):
        angle = math.pi / 4
        cone_plane = ConePlane(angle)
        self.assertEqual(cone_plane.cone_angle, angle)

        line_coords = [[0.0, 1.0, -3.0], [0.0, 0.5, 3.0]]
        angles = [0.0, 0.0, 0.0]

        intersect_point = cone_plane.plane_line_interesect(line_coords, angles)
        for point in intersect_point:
            # Extra check that point lies on cone
            check_val = self.check_is_on_cone(angle, point)
            self.assertAlmostEqual(check_val, 0)

        expected_point = [
            [0.0, 0.8181818181818182, -0.8181818181818181],
            [0.0, 0.6923076923076924, 0.6923076923076924],
        ]

        for i in range(len(intersect_point)):
            for j in range(len(intersect_point[i])):
                self.assertAlmostEqual(intersect_point[i][j], expected_point[i][j], 5)

    def test_cone_plane_get_line_angled_in_xyz_plane_intersect_points(self):

        angle = math.pi / 4
        cone_plane = ConePlane(angle)
        self.assertEqual(cone_plane.cone_angle, angle)

        line_coords = [[-3.0, 1.0, 0.0], [3.0, 0.5, 1.0]]
        angles = [0.0, 0.0, 0.0]

        intersect_point = cone_plane.plane_line_interesect(line_coords, angles)
        for point in intersect_point:
            # Extra check that point lies on cone
            check_val = self.check_is_on_cone(angle, point)
            self.assertAlmostEqual(check_val, 0)

        expected_point = [
            [-0.4849149568858915, 0.9274930204175537, 0.7906331560917682],
            [0.5184345099585173, 0.5977803724391613, 0.2976021380258791],
        ]

        for i in range(len(intersect_point)):
            for j in range(len(intersect_point[i])):
                self.assertAlmostEqual(intersect_point[i][j], expected_point[i][j], 5)


class TestConePlaneOnePointOutOfCone(unittest.TestCase):
    @staticmethod
    def check_is_on_cone(angle, point):
        """
        Should return 0.0 if a point lies on the cone, angle is the angle between the cone central axis
        and the surface
        """
        tan_ang = math.tan(angle)
        point = [p**2 for p in point]
        return point[1] * tan_ang**2 - point[0] - point[2]

    def test_cone_plane_get_simple_line_intersect_points(self):

        angle = math.pi / 4
        cone_plane = ConePlane(angle)
        self.assertEqual(cone_plane.cone_angle, angle)

        line_coords = [[0.0, 1.0, 0.0], [3.0, 1.0, 0.0]]
        angles = [0.0, 0.0, 0.0]

        intersect_point = cone_plane.plane_line_interesect(line_coords, angles)
        for point in intersect_point:
            # Extra check that point lies on cone
            check_val = self.check_is_on_cone(angle, point)
            self.assertAlmostEqual(check_val, 0)

        expected_point = [[1.0, 1.0, 0.0]]

        for i in range(len(intersect_point)):
            for j in range(len(intersect_point[i])):
                self.assertAlmostEqual(intersect_point[i][j], expected_point[i][j], 5)


if __name__ == "__main__":
    unittest.main()
