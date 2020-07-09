import unittest, sys, os

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

class TestConelane(unittest.TestCase):

    def test_get_line_equations_in_xy_plane(self):

        cone_plane = ConePlane(math.pi / 4)
        self.assertEqual(cone_plane.cone_angle, math.pi / 4)

        line_coords = [[-3.0, 1.0, 0.0], [3.0, 1.0, 0.0]]
        angles = [0.0, 0.0, 0.0]

        intersect_point = cone_plane.plane_line_interesect(line_coords, angles)
        expected_point = [1.0, 1.0, 0.0]
        
        for i in range(len(intersect_point)):
            self.assertAlmostEqual(intersect_point[i], expected_point[i], 5)

if __name__ == '__main__':
    unittest.main()