def draw_house(volumes, start_position=[0, 0, 0]):
    lines = []
    wall_left_vec = [0, 0, 6.0]
    wall_right_vec = [0, 0, 6.0]
    roof_left_vec = [-5.0, 0, 4.0]
    roof_right_vec = [5.0, 0, 4.0]

    for i in range(0, 10):
        y_pos = 5 + i
        wall_left_pos = sum_vectors([5.0, y_pos, 0.0], start_position)
        wall_right_pos = sum_vectors([-5.0, y_pos, 0.0], start_position)
        roof_left_pos = sum_vectors([5.0, y_pos, 6.0], start_position)
        roof_right_pos = sum_vectors([-5.0, y_pos, 6.0], start_position)
        lines.append(
            [
                wall_left_pos,
                sum_vectors(
                    wall_left_pos, scale_vector(wall_left_vec, 10 * volumes[0])
                ),
            ]
        )
        lines.append(
            [
                wall_right_pos,
                sum_vectors(
                    wall_right_pos, scale_vector(wall_right_vec, 10 * volumes[1])
                ),
            ]
        )
        lines.append(
            [
                roof_left_pos,
                sum_vectors(roof_left_pos, scale_vector(roof_left_vec, 1 * volumes[2])),
            ]
        )
        lines.append(
            [
                roof_right_pos,
                sum_vectors(
                    roof_right_pos, scale_vector(roof_right_vec, 1 * volumes[3])
                ),
            ]
        )
    return lines


def get_house_colours(volumes):
    colours = [
        [200 * volumes[0], 50 * volumes[0], 30 * volumes[1]],
        [200 * volumes[2], 50 * volumes[0], 200 * volumes[0]],
        [200 * volumes[3], 50 * volumes[1], 30 * volumes[2]],
        [100 * volumes[2], 200 * volumes[0], 30 * volumes[1]],
    ]

    return colours
