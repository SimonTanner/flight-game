import random

from physics.maths import *


class Grid:
    def __init__(self, position, fps, volumes):
        self.position = [0, 0, 0]
        # World position is where it will be when rendered
        self.world_position = position
        self.fps = fps
        self.geometry = []
        self.volumes = volumes
        self.init_colours = []
        self.colours = []
        self.initial_line_width = 3

        self.create_grid()
        self.rotator = Rotate()
        self.rotation_angle = [0, 0, 0]
        self.sync_rotation = True
        self.should_rotate = False

    def convert_list_float_to_ints(self, float_vec):
        return list(map(lambda a: int(a), float_vec))

    def create_grid(self):
        self.line_width = self.initial_line_width

        length = 5
        self.line_vectors = [
            [length, 0, 0],
            [-length, 0, 0],
            [0, -length, 0],
            [0, length, 0],
            [0, 0, length],
            [0, 0, -length],
        ]

        offset = 0.5
        self.line_vector_offsets_from_centre = [
            [offset, 0, 0],
            [-offset, 0, 0],
            [0, -offset, 0],
            [0, offset, 0],
            [0, 0, offset],
            [0, 0, -offset],
        ]

        for idx in range(0, len(self.line_vectors)):
            self.geometry.append(
                [
                    sum_vectors(
                        self.position, self.line_vector_offsets_from_centre[idx][:]
                    ),
                    scale_vector(
                        sum_vectors(self.position, self.line_vectors[idx][:]),
                        self.volumes[0],
                    ),
                ]
            )

        for _ in range(0, len(self.line_vectors)):
            delta = 100
            colour_shift = [
                random.random() * delta + 0,
                random.random() * delta + 70,
                random.random() * delta + 155,
            ]
            # print("color shift:", colour_shift)

            colour = self.convert_list_float_to_ints(colour_shift)
            self.init_colours.append(colour)
            self.colours = self.init_colours[:]

    def rotate_grid(self, point, volume=1):
        if self.should_rotate == True:
            if self.sync_rotation:
                volume = 1

            self.rotation_angle = sum_vectors(
                self.rotation_angle, [0, 0, math.pi / 180 * volume]
            )

            return self.rotator.rotate_data(
                point, self.rotation_angle, self.world_position
            )
        else:
            return point

    def update_grid(self, position_to_cam, volumes):
        self.geometry = []
        for idx in range(0, len(self.line_vectors)):
            self.geometry.append(
                [
                    sum_vectors(
                        self.world_position,
                        self.line_vector_offsets_from_centre[idx][:],
                    ),
                    self.rotate_grid(
                        sum_vectors(
                            self.world_position,
                            scale_vector(self.line_vectors[idx][:], volumes[idx]),
                        ),
                        volumes[idx],
                    ),
                ]
            )
        scale = self.get_scale_from_distance(position_to_cam)
        self.update_line_width(scale)
        self.update_colours(scale)
        # print("updated grid:", self.geometry)

    def get_scale_from_distance(self, position_to_cam):
        distance_vector = sum_vectors(
            self.world_position, position_to_cam, subtract=True
        )

        distance = scalar_product(distance_vector)
        scale = 1
        if distance > 20 and distance < 40:
            scale = 0.9

        elif distance > 40 and distance < 60:
            scale = 0.7

        elif distance > 60 and distance < 80:
            scale = 0.5

        elif distance > 80:
            scale = 0.3

        return scale

    def update_colours(self, scale):
        for idx in range(0, len(self.init_colours)):
            self.colours[idx] = self.convert_list_float_to_ints(
                scale_vector(self.init_colours[idx], scale)
            )

    def update_line_width(self, scale):
        l_width = int(self.initial_line_width * scale)
        if l_width == 0:
            l_width = 1
        self.line_width = l_width
        # print("line width:", self.line_width)

    def get_grid(self):
        return self.geometry

    def get_colours(self):
        return self.colours

    def get_line_width(self):
        return self.line_width

    def synchronise_rotation(self):
        self.sync_rotation = True if self.sync_rotation == False else False

    def set_should_rotate(self):
        self.should_rotate = True if self.should_rotate == False else False
