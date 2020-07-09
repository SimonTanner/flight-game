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
    """
    Returns the scalar product of a vector i.e. it's scalar length
    """
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

def get_point_distance(start_point, coords):
    vector = sum_vectors(coords, start_point, True)
    distance = scalar_product(vector)

    return distance

def get_plane(normal, vector):
    if abs(scalar_product(normal) - 1.0) > 0.000000001:
        normal = normalise_vector(normal)

    d = sum(map(lambda norm, perp: norm * perp, normal, vector))

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
        
        if delta_1 != 0.0 and delta_2 != 0.0:
            coeff = delta_2 / delta_1
            const = coord_2 - coord_1 * coeff
        elif delta_1 == 0.0:
            coeff = None
            const = coord_1
        elif delta_2 == 0.0:
            coeff = 0.0
            const = coord_2
        return coeff, const

    # Calc y = f(x)
    dy_dx, c_x = get_line_equation(dx, dy, x_1, y_1)

    # Calc z = f(y)
    dz_dy, c_y = get_line_equation(dy, dz, y_1, z_1)

    # Calc x = f(z)
    dx_dz, c_z = get_line_equation(dz, dx, z_1, x_1)

    equations = {
        "y_x": {"coeff": dy_dx, "const": c_x},
        "z_y": {"coeff": dz_dy, "const": c_y},
        "x_z": {"coeff": dx_dz, "const": c_z},
    }

    return equations

def apply_equation(coord, eqns, key):
    coeff, const = eqns[key]["coeff"], eqns[key]["const"]
    if coeff != None:
        val = coeff * coord + const
    else:
        val = const
    
    return val

def plane_line_interesect(plane, line_eqns, is_flat=True):
    """
    Calculates the intersection coordinates for a line and a plane equation
    """
    mapping = {
        "y_x": {
            "eqn": "y_x",
            "inv_eqn": "x_z",
            "plane_coeffs": ["x", "y", "z"],
            "line_eqns": ["y_x", "z_y", "z_x"]
        },
        "z_y": {
            "eqn": "z_y",
            "inv_eqn": "y_x",
            "plane_coeffs": ["y", "z", "x"],
            "line_eqns": ["z_y", "x_z", "y_x"]
        },
        "x_z": {
            "eqn": "x_z",
            "inv_eqn": "z_y",
            "plane_coeffs": ["z", "x", "y"],
            "line_eqns": ["x_z", "y_x", "z_y"]
        },
    }
    coord = None
    eqn_used = ""
    coords = {
        "x": None,
        "y": None,
        "z": None
    }

    axis_order = [
        "x",
        "y",
        "z"
    ]

    # mapping to show which value has been found from the given equation
    axes_to_eqn = {
        "y_x": "y",
        "z_y": "z",
        "x_z": "x"
    }

    # mapping to show which value has been found by inverting the given equation
    axis_invert = {
        "y_x": "x",
        "z_y": "y",
        "x_z": "z"
    }

    eqns_to_calc = []

    # Firstly if any coefficients are 0.0 or None (i.e.) infinity we know the values are always just the consts
    for eqn in line_eqns.keys():
        coeff, const = line_eqns[eqn]["coeff"], line_eqns[eqn]["const"]
        if coeff is None:
            axis = axis_invert[eqn]
            coords[axis] = const
        elif coeff == 0.0:
            axis = axes_to_eqn[eqn]
            coords[axis] = const
        else:
            eqns_to_calc.append(eqn)

    found_count = 0
    for value in coords.values():
        # Check which coords need to be found
        if value != None:
            found_count +=1

    if found_count == 2:
        # Case we already have 2 coords i.e due to 2 eqns of the form y = constant
        coords = get_last_intersect_coord(plane, coords)
    elif found_count == 1:
        # Case we only have 1 coord
        eqn = eqns_to_calc[0]
        axis = axes_to_eqn[eqn]
        coords[axis] = get_intersect_coord(mapping[eqn], plane, line_eqns)
        coords = get_last_intersect_coord(plane, coords)

    else:
        for eqn in mapping.keys():
            axis = mapping[eqn]["plane_coeffs"][0]
            if line_eqns[eqn]["coeff"] == None:
                axis = axis_invert[eqn]
                coords[axis] = line_eqns[eqn]["const"]

            else:
                coords[axis] = get_intersect_coord(mapping[eqn], plane, line_eqns)

    values = [coords[axis] for axis in axis_order]

    return values

def get_intersect_coord(map_dict, plane, line_eqns): 
    plane_1, plane_2, plane_3 = map_dict["plane_coeffs"]
    inv_eqn = invert_equation(line_eqns[map_dict["inv_eqn"]])
    eqn = line_eqns[map_dict["eqn"]]
    if inv_eqn["coeff"] != None:
        numerator = (
            plane["D"] - plane[plane_2] * eqn["const"] + plane[plane_3] * inv_eqn["const"]
        )
        axis_val =  numerator / (
            plane[plane_1] + plane[plane_2] * eqn["coeff"] + plane[plane_3] * inv_eqn["coeff"]
        )
    else:
        axis_val = None

    return axis_val

def invert_equation(eqn):
    coeff, const = eqn["coeff"], eqn["const"]
    if coeff != None and coeff != 0.0:
        inv_eqn = {
            "coeff": 1 / coeff,
            "const": const / coeff
        }
    elif coeff == None:
        inv_eqn = {
            "coeff": 0.0,
            "const": const
        }
    else:
        inv_eqn = {
            "coeff": None,
            "const": const
        }

    return inv_eqn

def get_last_intersect_coord(plane, coords):
    """
    Given a set of equations where two have coefficient as None then we already have two values
    and can easily calculate the 3rd using the 2 coords & the plane equation
    """
    axes_found = []
    for axis, value in coords.items():
        if value is None:
            axis_to_find = axis
        else:
            axes_found.append(axis)
    total = 0.0

    for axis in axes_found:
        total += plane[axis] * coords[axis]
    coords[axis_to_find] = (plane["D"] - total) / plane[axis_to_find]

    return coords

# def get_point_along_line(eqn, vertices, angles):
#     """
#     Calculates the position along a line at a given angle from a point
#     """


def check_coords_in_plane(plane, coords):
    """
    Simple checker for a point of intersection and a plane equation
    """
    D = plane["D"]
    d = plane["x"] * coords[0] + plane["y"] * coords[1] + plane["z"] * coords[2]
    return D, d

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

def normalise_vector(vector):
    length = scalar_product(vector)
    normal = list(map(lambda a: a / length, vector))

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

def scale_vector(vector, scale):
    scaled_vector = list(map(lambda a: a * scale, vector))

    return scaled_vector

def vector_ang(vec_1, vec_2, in_degrees=True):
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

        except ValueError:
            cos_ang_1 = 0.0
            break

        else:
            break
    if in_degrees is True:
        ang_1 = math.degrees(math.acos(cos_ang_1))
    else:
        ang_1 = math.acos(cos_ang_1)

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
    
        self.rotate_matrix = [rotate_x, rotate_y, rotate_z]

    def rotate_data(self, coords, angle, offset=[0, 0, 0]):
        """
        Rotates vectors about the offset point
        """
        translated_point = sum_vectors(coords, offset, True)

        def apply_matrix(matrix, angle, coords):
            coords = list(map(lambda a: sum(map(lambda b, c: b[0](angle) * b[1] * c, a, coords)), matrix))
            return coords

        for idx in range(0, len(angle)):
            if angle[idx] != 0:
                translated_point = apply_matrix(self.rotate_matrix[idx], angle[idx], translated_point)

        coords = list(sum_vectors(offset, translated_point))

        return coords

    def unrotate_data(self, coords, angle, offset=[0, 0, 0]):
        """
        Rotates vectors about the offset point back to before it was rotated
        """
        translated_point = sum_vectors(coords, offset, True)

        def apply_matrix(matrix, angle, coords):
            coords = list(map(lambda a: sum(map(lambda b, c: b[0](angle) * b[1] * c, a, coords)), matrix))
            return coords

        for idx in range(len(angle) - 1, -1, -1):
            if angle[idx] != 0:
                translated_point = apply_matrix(self.rotate_matrix[idx], -1 * angle[idx], translated_point)

        coords = list(sum_vectors(offset, translated_point))

        return coords

class ConePlane():
    def __init__(self, cone_angle):
        self.rotate = Rotate()
        self.cone_angle = cone_angle
        self.tan_ang_sqrd = math.tan(self.cone_angle) ** 2
        self.mapping = {
            "y_x": {
                "eqn": "y_x",
                "inv_eqn": "x_z",
                "plane_coeffs": ["x", "y", "z"],
                "line_eqns": ["y_x", "z_y", "z_x"]
            },
            "z_y": {
                "eqn": "z_y",
                "inv_eqn": "y_x",
                "plane_coeffs": ["y", "z", "x"],
                "line_eqns": ["z_y", "x_z", "y_x"]
            },
            "x_z": {
                "eqn": "x_z",
                "inv_eqn": "z_y",
                "plane_coeffs": ["z", "x", "y"],
                "line_eqns": ["x_z", "y_x", "z_y"]
            },
        }
        self.axis_order = [
            "x",
            "y",
            "z"
        ]

        # mapping to show which value has been found from the given equation
        self.axes_to_eqn = {
            "y_x": "y",
            "z_y": "z",
            "x_z": "x"
        }

        # mapping to show which value has been found by inverting the given equation
        self.axis_invert = {
            "y_x": "x",
            "z_y": "y",
            "x_z": "z"
        }

    def _get_equations(self, coords, angle):
        self.rotated_coords = []
        for coord in coords:
            self.rotated_coords.append(self.rotate.unrotate_data(coord, angle))
        self.equations = get_line_equations(self.rotated_coords[0], self.rotated_coords[1])

    def _get_intersect_coord(self, mapping):
        """
        Get the value of an axis at the point of intersection between a line and a conical plane
        """
        inv_eqn = invert_equation(self.line_equations[mapping["inv_eqn"]])
        eqn = self.line_equations[mapping["eqn"]]

        if inv_eqn["coeff"] != None:
            coeff_sqrd = eqn["coeff"] ** 2
            const_sqrd = eqn["const"] ** 2
            inv_coeff_sqrd = inv_eqn["const"] ** 2
            inv_const_sqrd = inv_eqn["const"] ** 2
            alpha = coeff_sqrd * self.tan_ang_sqrd - inv_coeff_sqrd ** 2 - 1
            beta = eqn["coeff"] * eqn["const"] * self.tan_ang_sqrd - inv_eqn["const"]

            sqr_to_check = inv_const_sqrd - const_sqrd * self.tan_ang_sqrd + beta ** 2
            if sqr_to_check > 0.0:
                # TODO - figure out how to know whether to subtract or add due to square root
                axis_val = (-beta + math.sqrt(sqr_to_check)) / alpha
            else:
                axis_val = None
        else:
            axis_val = None

        return axis_val

    def _get_last_intersect_coord(self, coords):
        """
        Given a set of equations where two have coefficient as None then we already have two values
        and can easily calculate the 3rd using the 2 coords & the plane equation
        """
        axes_found = []
        total = 0.0
        x_z_axes = ["x", "z"]
        print(coords)

        for axis, value in coords.items():
            if value is None:
                axis_to_find = axis
            else:
                axes_found.append(axis)

        if axis_to_find == "y":
            # Because the cone is aligned with the y axis the plane has the coefficient
            # tan^2(angle)
            for axis in axes_found:
                total += coords[axis] ** 2

            coords[axis_to_find] = math.sqrt(total / self.tan_ang_sqrd)

        elif axis_to_find in x_z_axes:
            del(x_z_axes[x_z_axes.index(axis_to_find)])
            other_axis = x_z_axes[0]
            print(other_axis)
            print(axis_to_find)
            coords[axis_to_find] = math.sqrt(coords["y"] ** 2 * self.tan_ang_sqrd - coords[other_axis] ** 2)

        

        return coords

    def plane_line_interesect(self, coords, angle):
        """
        Calculates the intersection coordinates for a line and a plane equation. The angle is a list of the angles between
        the y axis, because the cone is set in the y direction for simplicity
        """
        self._get_equations(coords, angle)

        intersect_coords = {
            "x": None,
            "y": None,
            "z": None
        }

        eqns_to_calc = []

        # Firstly if any coefficients are 0.0 or None (i.e.) infinity we know the values are always just the consts
        for eqn in self.equations.keys():
            coeff, const = self.equations[eqn]["coeff"], self.equations[eqn]["const"]
            if coeff is None:
                axis = self.axis_invert[eqn]
                intersect_coords[axis] = const
            elif coeff == 0.0:
                axis = self.axes_to_eqn[eqn]
                intersect_coords[axis] = const
            else:
                eqns_to_calc.append(eqn)

        found_count = 0
        for value in intersect_coords.values():
            # Check which coords need to be found
            if value != None:
                found_count +=1

        if found_count == 2:
            # Case we already have 2 coords i.e due to 2 eqns of the form y = constant
            intersect_coords = self._get_last_intersect_coord(intersect_coords)
        elif found_count == 1:
            # Case we only have 1 coord
            eqn = eqns_to_calc[0]
            axis = self.axes_to_eqn[eqn]
            intersect_coords[axis] = self._get_intersect_coord(self.mapping[eqn])
            intersect_coords = self._get_last_intersect_coord(intersect_coords)

        else:
            for eqn in self.mapping.keys():
                axis = self.mapping[eqn]["plane_coeffs"][0]
                if self.equations[eqn]["coeff"] == None:
                    axis = self.axis_invert[eqn]
                    intersect_coords[axis] = self.equations[eqn]["const"]

                else:
                    intersect_coords[axis] = self._get_intersect_coord(self.mapping[eqn])

        values = [intersect_coords[axis] for axis in self.axis_order]

        return values