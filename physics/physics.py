import math

def calc_surface_drag(surface, velocity, density):
    surf_area, perp_vector = calc_surface_area(surface)
    coeff_drag = vector_ang(perp_vector, velocity)
    drag = scalar_product(velocity) ** 2 * coeff_drag * density * surf_area / 2

    return drag

    
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

def sum_vectors(vec_1, vec_2, subtract=False):
    """
    Adds vec_1 & vec_2 or Subtracts vec_2 from vec_1
    """
    if subtract:
        vec_sum = map(lambda a, b: a - b, vec_1, vec_2)
    else:
        vec_sum = map(lambda a, b: a + b, vec_1, vec_2)

    return(vec_sum)

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

