import random

from physics.maths import *


class Grid:
    def __init__(self, position, ffps, volumes):
        self.position = position
        self.ffps = ffps
        self.geometry = []
        self.volumes = volumes
        self.colours = []
        self.create_grid()
        self.rotator = Rotate()
        self.rotation_angle = [0, 0, 0]

    def create_grid(self):
        self.line_vectors = [
            [5, 0, 0],
            [-5, 0, 0],
            [0, -5, 0],
            [0, 5, 0],
            [0, 0, 5],
            [0, 0, -5],
        ]

        for line_vector in self.line_vectors:
            self.geometry.append(
                [
                    self.position,
                    scale_vector(
                        sum_vectors(self.position, line_vector), self.volumes[0]
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

            colour = list(map(lambda a: int(a), colour_shift))
            self.colours.append(colour)

    def transform_geometry(self, point):
        self.rotation_angle = sum_vectors(self.rotation_angle, [0, 0, math.pi / 360])
        return self.rotator.rotate_data(point, self.rotation_angle, self.position)

    def update_grid(self, volumes):
        self.geometry = []
        for idx in range(0, len(self.line_vectors)):
            self.geometry.append(
                [
                    self.position,
                    self.transform_geometry(
                        sum_vectors(
                            self.position,
                            scale_vector(self.line_vectors[idx][:], volumes[idx]),
                        )
                    ),
                ]
            )
        # print("updated grid:", self.geometry)

    def get_grid(self):
        return self.geometry

    def get_colours(self):
        return self.colours
