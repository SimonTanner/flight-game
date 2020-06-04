import math

def calc_surface_drag(surface, velocity, density):
    surf_area, perp_vector = calc_surface_area(surface)
    coeff_drag = vector_ang(perp_vector, velocity)
    drag = scalar_product(velocity) ** 2 * coeff_drag * density * surf_area / 2

    return drag
