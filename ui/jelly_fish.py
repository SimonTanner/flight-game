import random

from physics.maths import *


class JellyFish:
    def __init__(self, position, fps, volumes):
        self.type = "jelly_fish"
        self.position = [0, 0, 0]
        # length along the y axis for ease.
        self.length = 60
        self.width = 30
        self.num_sides = 12
        self.no_joints = 30
        # World position is where it will be when rendered
        self.world_position = position
        self.jelly_fish_position = self.position
        self.move_numerator = 60
        self.should_expand = True

        self.fps = fps
        self.geometry = []
        self.volumes = volumes
        self.init_colours = []
        self.colours = []
        self.initial_line_width = 3
        self.undulation_speed = 0.4
        self.counter = 0

        self.rotator = Rotate()
        self.create()

        self.rotation_angle = [0, 0, 0]
        self.sync_rotation = True
        self.should_rotate = False

    def convert_list_float_to_ints(self, float_vec):
        return list(map(lambda a: int(a), float_vec))

    def generate_coords(self, idx, line_length):
        y = idx * line_length

        delta_z = math.sin((math.pi * y) / (self.length))
        z = self.width * delta_z + (
            delta_z
            * (self.width / 5)
            * math.sin(
                (3 * math.pi * y) / (self.length)
                + (self.undulation_speed * self.counter)
            )
        )

        return [0, y, z]

    def generate_gemoetry(self):
        self.geometry = []
        self.line_width = self.initial_line_width
        line_length = self.length / self.no_joints

        for i in range(0, self.no_joints):

            p1 = self.generate_coords(i, line_length)
            p2 = self.generate_coords(i + 1, line_length)

            self.geometry.append([p1, p2])

        first_side = self.geometry[:]
        y_ang = math.pi * 2 / self.num_sides

        for side_no in range(0, self.num_sides):
            for line in first_side:
                rotated_line = []
                for point in line:
                    rotated_line.append(
                        self.rotator.rotate_data(point, [0, side_no * y_ang, 0])
                    )
                self.geometry.append(rotated_line)

        # print(len(self.geometry))

    def create(self):
        print(1)
        self.generate_gemoetry()

        for i in range(0, self.no_joints):
            delta = 70
            colour_shift = [
                random.random() * delta + 0,
                math.sin((math.pi * i) / self.no_joints) * delta + 185,
                math.cos((math.pi * i) / self.no_joints) * delta + 185,
            ]
            # print("color shift:", colour_shift)

            colour = self.convert_list_float_to_ints(colour_shift)
            self.init_colours.append(colour)
            self.colours = self.init_colours[:]

        for _ in range(0, self.num_sides):
            self.colours = self.colours + self.init_colours[:]

        # print(self.geometry)
        # print(len(self.geometry))
        # print(self.colours)
        # print(len(self.colours))

    def rotate(self, point, volume=1):
        pass

    def expand(self):
        pass

    def update(self, position_to_cam, volumes):
        self.counter += 1
        self.generate_gemoetry()

    def get_scale_from_distance(self, position_to_cam):
        pass

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

    def get_geometry(self):
        return self.geometry

    def get_colours(self):
        return self.colours

    def get_line_width(self):
        return self.line_width

    def synchronise_rotation(self):
        self.sync_rotation = True if self.sync_rotation == False else False

    def set_should_rotate(self):
        self.should_rotate = True if self.should_rotate == False else False

    def toggle_expand(self):
        if self.move_counter <= self.move_numerator:
            self.should_expand = True
            self.should_contract = False

        elif self.move_counter > 0:
            self.should_expand = False
            self.should_contract = True
