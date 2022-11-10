import math

from .maths import *


def calc_surface_drag(surface, velocity, density):
    surf_area, perp_vector = calc_surface_area(surface)
    coeff_drag = vector_ang(perp_vector, velocity)
    drag = scalar_product(velocity) ** 2 * coeff_drag * density * surf_area / 2

    return drag


def get_accel_vector(force_vector, mass):
    accel_vec = scale_vector(force_vector, 1 / mass)
    return accel_vec


def get_velocity_change(force_vector, mass, dt):
    a = [0.0, 0.0, -9.81]
    a2 = get_accel_vector(force_vector, mass)
    accel = sum_vectors(a, a2)
    velocity_vector = scale_vector(accel, dt)

    return velocity_vector
