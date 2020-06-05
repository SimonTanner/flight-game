import math


def calc_surface_area(surface):
    no_verts = len(surface)
    area = 0
    perp_vector = []
    for idx in range(0, no_verts, 2):
        vector_1 = sum_vectors(surface[idx], surface[idx + 1], True)
        vector_2 = sum_vectors(surface[idx + 2], surface[idx + 1], True)
        area += vector_area(vector_1, vector_2)
        if idx == 0:
            perp_vector = cross_product(vector_1, vector_2)
    return area, perp_vector     


def scalar_product(vector):
    scalar = math.sqrt(sum(map(lambda a: a**2, vector)))
    return scalar

def vector_area(vector_1, vector_2):
    cross_prod = cross_product(vector_1, vector_2)
    area = scalar_product(cross_prod) / 2
    return area

def dot_product(vector_1, vector_2):
    dot_prod = list(map(lambda a, b: a * b, vector_1, vector_2))
    
    return dot_prod

def cross_product(vector_1, vector_2):
    cross_prod = []
    idx_rule = {
        0: [1, 2],
        1: [2, 0],
        2: [0, 1]
    }

    for idx in range(0, 3):
        idx_1, idx_2 = idx_rule[idx]
        coeff = vector_1[idx_1] * vector_2[idx_2] - vector_1[idx_2] * vector_2[idx_1]
        cross_prod.append(coeff)

    return cross_prod

def get_plane(normal, perp_vector):
    d = sum(map(lambda norm, perp: norm * perp, normal, perp_vector))

    equation = {"D": d, "x": normal[0], "y": normal[1], "z": normal[2]}

    return equation

def get_line_equations(point_1, point_2):
    """
    Calculates line equations and returns dict object with each set
    """
    x_1, x_2 = point_1[0], point_2[0]
    y_1, y_2 = point_1[1], point_2[1]
    z_1, z_2 = point_1[2], point_2[2]

    dx = x_1 - x_2
    dy = y_1 - y_2
    dz = z_1 - z_2

    def get_line_equation(delta_1, delta_2, coord_1, coord_2):
        # Calculates line equation and handles infinite or zero delta_2 / delta_1
        # returning None as the coefficient if infinite
        
        if delta_1 != 0 and delta_2 != 0:
            coeff = delta_2 / delta_1
            const = coord_2 - coord_1 * coeff
        elif delta_1 == 0:
            coeff = None
            const = coord_1
        elif delta_2 == 0:
            coeff = 0
            const = coord_2
        return coeff, const

    # Calc y = f(x)
    dy_dx, c_x = get_line_equation(dx, dy, x_1, y_1)

    # Calc z = f(y)
    dz_dy, c_y = get_line_equation(dy, dz, y_1, z_1)

    # Calc x = f(z)
    dx_dz, c_z = get_line_equation(dz, dx, z_1, x_1)

    equations = {
        "xy": {"coeff": dy_dx, "const": c_x},
        "yz": {"coeff": dz_dy, "const": c_y},
        "zx": {"coeff": dx_dz, "const": c_z},
    }

    return equations

# def plane_line_interesect(plane, line):
#     """
#     Calculates the intersection coordinates for a line and a plane equation
#     """
    

def get_normal(vector_1, vector_2):
    perp_vector = cross_product(vector_1, vector_2)
    length = scalar_product(perp_vector)
    if length <= 0.0:
        print("---------get_normal---------")
        print(vector_1)
        print(vector_2)
        print("---------get_normal---------")
    normal = list(map(lambda a: a / length, perp_vector))

    return normal

def sum_vectors(vec_1, vec_2, subtract=False):
    """
    Adds vec_1 & vec_2 or Subtracts vec_2 from vec_1
    """
    if subtract:
        vec_sum = list(map(lambda a, b: a - b, vec_1, vec_2))
    else:
        vec_sum = list(map(lambda a, b: a + b, vec_1, vec_2))

    return vec_sum

def vector_ang(vec_1, vec_2):
    """
    Calculate the angle between two vectors
    """
    # While loop added due to value error generated if two vectors were the same but float nums
    while True:
        try:
            dot_prod = sum(map(lambda a, b: a * b, vec_1, vec_2))
            mod_vec_1 = math.sqrt(sum(map(lambda c: c**2, vec_1)))
            mod_vec_2 = math.sqrt(sum(map(lambda c: c**2, vec_2)))
            cos_ang_1 = dot_prod / (mod_vec_1 * mod_vec_2)
            ang_1 = math.degrees(math.acos(cos_ang_1))

        except ValueError:
            ang_1 = 0.0
            break

        else:
            break

    return(ang_1)

class Rotate():
    def __init__(self):
        self._create_rotation_matrix()

    def _create_rotation_matrix(self):
        # Rotational matrices around axes x, y, z
        cos = math.cos
        sin = math.sin

        def return_0(val, neg=False):
            return 0
        
        def return_1(val, neg=False):
            return 1

        rotate_x = [
            [(return_1, 1), (return_0, 1), (return_0, 1)],
            [(return_0, 1), (cos, 1), (sin, -1)],
            [(return_0, 1), (sin, 1), (cos, 1)]
        ]

        rotate_y = [
            [(cos, 1), (return_0, 1), (sin, 1)],
            [(return_0, 1), (return_1, 1), (return_0, 1)],
            [(sin, 1), (return_0, 1), (cos, 1)]
        ]

        rotate_z = [
            [(cos, 1), (sin, -1), (return_0, 1)],
            [(sin, 1), (cos, 1), (return_0, 1)],
            [(return_0, 1), (return_0, 1), (return_1, 1)]
        ]
    
        self.rotate = [rotate_x, rotate_y, rotate_z]

    def rotate_data(self, coords, angle, offset=[0, 0, 0]):
        """
        Rotates vectors about the offset point
        """
        translated_point = sum_vectors(coords, offset, True)

        def apply_matrix(matrix, angle, coords):
            angle = math.radians(angle)
            coords = list(map(lambda a: sum(map(lambda b, c: b[0](angle) * b[1] * c, a, coords)), matrix))
            return coords

        for idx in range(0, len(angle)):
            if angle[idx] != 0:
                translated_point = apply_matrix(self.rotate[idx], angle[idx], translated_point)

        coords = list(sum_vectors(offset, translated_point))

        return coords


# def get_equation(start_point, end_point):
