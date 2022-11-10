import pygame, sys, math, random, traceback, json, os, time, threading
from pygame.locals import *

# sys.path.append(os.getcwd())
sys.path.append("/home/simon/python/flight-game/physics")
from physics.maths import *
from physics.physics import *

from ui.grid import Grid


class Game:
    def __init__(self, screen_dims=[1800, 1000], volumes=[1, 1, 1, 1, 1, 1, 1, 1]):
        self.screen_dims = screen_dims
        self.fps = 30  # Frame rate
        self.fps_clock = pygame.time.Clock()
        self.bkgrnd_colour = (0, 0, 0)
        self.line_colour = (200, 50, 50)

        # Instantiate rotation function
        self.rotate = Rotate()

        # Camera constants
        self.camera_position = [0.01, -10.0, 2.0]
        # Field of View angle
        self.fov_ang = math.pi / 2
        # angle between the z-axis and the centre of view
        self.camera_start_ang = [-math.pi / 6, 0, 0]
        self.cam_ang_rate = math.pi / (self.fps * 5)
        # Perpendicular distance from camera to clipping plane
        self.dist_clip_plane = 0.5
        self.initialise_camera()
        self.get_max_visible_angle()

        # Instantiate cone interesect function
        self.view_cone = ConePlane(self.fov_ang / 2)

        self.light_direction = [1.0, 2.0, -1.0]

        # Consts for initialising ship
        self.start_angle_ship = [0.0, 0.0, 0.0]
        self.ship_angle = [0, 0, 0]
        self.ship_start_pos = [-0.0, 0.0, 0.5]
        self.ship_velocity = [0.0, 0.0, 0.0]
        self.ship_base_colour = (200, 50, 150)
        self.ship_turn_rate = math.pi / (self.fps * 5)
        self.hover = False
        self.align_cam_to_ship = True

        self.time_rate = 1 / self.fps
        self.lines = create_test_data()
        self.volumes = volumes
        # self.house = draw_house([0, 0, 0], volumes)
        self.create_grids()

    def initialise_camera(self):
        self.init_cp_normal = list(
            map(
                lambda coord: coord / self.dist_clip_plane,
                [0.0, self.dist_clip_plane, 0.0],
            )
        )
        half_fov_ang = self.fov_ang / 2
        # Get the normal for the RHS clipping plane -> rotate the clipping plane normal about the z axis.
        self.init_cp_normal_right = self.rotate.rotate_data(
            self.init_cp_normal, [0, 0, half_fov_ang]
        )
        # Get the normal for the LHS clipping plane -> rotate the clipping plane normal about the z axis.
        self.init_cp_normal_left = self.rotate.rotate_data(
            self.init_cp_normal, [0, 0, -half_fov_ang]
        )
        # Get the normal for the top clipping plane -> rotate the clipping plane normal about the x axis.
        self.init_cp_normal_top = self.rotate.rotate_data(
            self.init_cp_normal, [half_fov_ang, 0, 0]
        )
        # Get the normal for the bottom clipping plane -> rotate the clipping plane normal about the x axis.
        self.init_cp_normal_bottom = self.rotate.rotate_data(
            self.init_cp_normal, [-half_fov_ang, 0, 0]
        )

        self.cp_normal_right = self.init_cp_normal_right
        self.cp_normal_left = self.init_cp_normal_left
        self.cp_normal_top = self.init_cp_normal_top
        self.cp_normal_bottom = self.init_cp_normal_bottom

        # Rotate all normals to align with the starting camera angle.
        self.camera_ang = self.camera_start_ang
        self.rotate_clipping_plane_normals(self.camera_ang)

        self.init_perp_cp_vector()
        # print(self.perp_vec_cp)
        self.get_clip_plane()

    def get_max_visible_angle(self):
        max_h = math.tan(self.fov_ang / 2)
        scr_ratio_angle = math.atan(self.screen_dims[0] / self.screen_dims[1])
        self.max_vis_angle = math.atan(max_h / math.cos(scr_ratio_angle))

    def init_perp_cp_vector(self):
        self.init_perp_vec_cp = self.rotate.rotate_data(
            self.cp_normal, (0, 0, math.pi / 2)
        )
        self.perp_vec_cp = self.init_perp_vec_cp

    def get_clip_plane(self):
        self.cp_centre_point = self.cp_normal
        self.blah_point = sum_vectors(self.cp_centre_point, self.perp_vec_cp)
        self.clip_plane = get_plane(self.cp_normal, self.blah_point)

    def rotate_clipping_plane_normals(self, angle, all_normals=True):
        self.cp_normal = self.rotate.rotate_data(self.init_cp_normal, angle)
        if all_normals:
            self.cp_normal_right = self.rotate.rotate_data(
                self.init_cp_normal_right, angle
            )
            self.cp_normal_left = self.rotate.rotate_data(
                self.init_cp_normal_left, angle
            )
            self.cp_normal_top = self.rotate.rotate_data(self.init_cp_normal_top, angle)
            self.cp_normal_bottom = self.rotate.rotate_data(
                self.init_cp_normal_bottom, angle
            )

    def rotate_camera(self, angle):
        """
        Rotates the camera and calculates the new clipping plane, it's normal and perpendicular vector
        """
        # sum the previous camera angle with the new angle of rotation
        self.camera_ang = sum_vectors(self.camera_ang, angle)
        # print(self.camera_ang)
        self.rotate_clipping_plane_normals(self.camera_ang)
        self.perp_vec_cp = self.rotate.rotate_data(
            self.init_perp_vec_cp, self.camera_ang
        )

        self.get_clip_plane()

    def convert_to_perspective(self, objs, is_dict=False):
        """
        convert geometry coordinates into perspective screen coordinates
        """

        # Calculate the height of the clipping plane that all points are projected onto
        # In order to get the required scale for converting to the screen coordinates
        self.plane_height = math.tan(self.fov_ang / 2) * 2
        scr_scale = self.screen_dims[1] / self.plane_height

        converted_coords = []

        for obj in objs:
            screen_coords = []
            points_vis = []
            coords_to_point = []
            angles_from_cp_normal = []
            # print("--------------------------------------------------")

            # Check whether it's a shape or a line.
            if is_dict:
                coords = obj["coords"]
            else:
                coords = obj

            for coord in coords:
                # Get the relative coordinates to the camera position.
                coord_to_point = [i - j for i, j in zip(coord, self.camera_position)]
                coords_to_point.append(coord_to_point)

                # Check if the point is infront or behind the clipping plane
                vector_angle = vector_ang(coord_to_point, self.cp_normal, False)
                angles_from_cp_normal.append(vector_angle)
                # print("angle to point:", vector_angle)
                # print("max vis angle:", self.max_vis_angle)
                # print("y coord:", coord_to_point[1])

                is_in_view = True if vector_angle < self.max_vis_angle else False
                # print("is_n_view:", is_in_view)
                points_vis.append(is_in_view)

            if True not in points_vis:
                # If no coords are visible we don't calculate
                pass

            else:
                # print("points_vis:", points_vis)
                if False in points_vis:
                    # In this case a point might be out of view but all other points are in view
                    coords_to_point = self._get_plane_object_intersection(
                        coords_to_point, points_vis, angles_from_cp_normal
                    )

                for coord_to_point in coords_to_point:
                    # is_in_view = True if vector_ang(coord_to_point, self.cp_normal) < 90 else False

                    # if is_in_view:
                    line_eqns = get_line_equations((0, 0, 0), coord_to_point)

                    intersect_coords = plane_line_interesect(self.clip_plane, line_eqns)

                    # Get coords relative to camera centre point in the clipping plane
                    relative_coords = sum_vectors(
                        intersect_coords, self.cp_centre_point, True
                    )
                    # Rotate these back to get the values required in the 2D plane
                    plane_coords = self.rotate.unrotate_data(
                        relative_coords, self.camera_ang
                    )
                    # plane_coords = relative_coords

                    delta_xy_in_vp = plane_coords[0]
                    delta_yz_in_vp = plane_coords[2]

                    scr_coord_x = round(
                        self.screen_dims[0] / 2 - delta_xy_in_vp * scr_scale
                    )
                    scr_coord_y = round(
                        self.screen_dims[1] / 2 - delta_yz_in_vp * scr_scale
                    )

                    screen_coords.append([scr_coord_x, scr_coord_y])

            if len(screen_coords) >= 2:
                converted_coords.append(screen_coords)

        return converted_coords

    def get_perspective_intersection_plane(self, visible_coord, invisible_coord):
        """
        Function to find which plane to use when a 1 point of a line is out of view
        """
        xz_ratio = self.screen_dims[1] / self.screen_dims[0]
        max_x = invisible_coord[1] / math.tan(self.fov_ang / 2)
        # print("max angle z:", self.fov_ang * xz_ratio / 2)
        max_z = max_x * xz_ratio

        min_x = -max_x
        min_z = -max_z

        line_dx = invisible_coord[0] - visible_coord[0]
        line_dz = invisible_coord[2] - visible_coord[2]
        if line_dx != 0:
            if line_dz == 0:
                # if 0 < line_dx:
                #     angle = 0
                # if 0 > line_dx:
                angle = 0
            else:
                angle = math.atan(line_dz / line_dx)
        else:
            angle = math.pi / 2

        if line_dx >= 0 and line_dz >= 0:
            # positive x, positive z quadrant
            max_dx = max_x - visible_coord[0]
            max_dz = max_z - visible_coord[2]
            max_angle = math.atan(max_dz / max_dx)
            if angle >= max_angle:
                # print("self.cp_normal_top")
                return self.cp_normal_top
            else:
                # print("self.cp_normal_right")
                return self.cp_normal_right

        elif line_dx <= 0 and line_dz >= 0:
            # negative x, positive z quadrant
            max_dx = min_x - visible_coord[0]
            max_dz = max_z - visible_coord[2]
            max_angle = math.atan(max_dz / max_dx)
            if angle <= max_angle:
                # print("self.cp_normal_top")
                return self.cp_normal_top
            else:
                # print("self.cp_normal_left")
                return self.cp_normal_left

        elif line_dx <= 0 and line_dz <= 0:
            # negative x, negative z quadrant
            max_dx = min_x - visible_coord[0]
            max_dz = min_z - visible_coord[2]
            max_angle = math.atan(max_dz / max_dx)

            if angle >= max_angle:
                # print("self.cp_normal_bottom")
                return self.cp_normal_bottom
            else:
                # print("self.cp_normal_left")
                return self.cp_normal_left

        elif line_dx >= 0 and line_dz <= 0:
            # positive x, negative z quadrant
            max_dx = max_x - visible_coord[0]
            max_dz = min_z - visible_coord[2]
            max_angle = math.atan(max_dz / max_dx)

            if angle <= max_angle:
                # print("self.cp_normal_bottom")
                return self.cp_normal_bottom
            else:
                # print("self.cp_normal_right")
                return self.cp_normal_right

        # print(
        #     "angle:",
        #     angle * 180 / math.pi,
        #     "\nmax angle:",
        #     max_angle * 180 / math.pi,
        #     "\nline dx:",
        #     line_dx,
        #     "\nline dz:",
        #     line_dz,
        #     "\nmax_x:",
        #     max_x,
        #     "\nmax_z:",
        #     max_z,
        #     "\nmax_dx:",
        #     max_dx,
        #     "\nmax_dz:",
        #     max_dz,
        #     "\n\n",
        # )

    def _get_plane_object_intersection(self, coords, points_vis, angles_from_cp_normal):
        """
        If a point is out of view, recalculate this point as the intersection between the line
        equation connecting these points and the intersection point between this and the clipping plane
        """

        idx = points_vis.index(False)
        no_vertices = len(coords)
        # if no_vertices > 2:
        #     print(coords)
        #     print(points_vis)

        new_coords = []
        start_val = idx - 1 if idx - 1 >= 0 else no_vertices - 1
        end_val = idx + 1 if idx + 1 <= no_vertices - 1 else 0

        if start_val != end_val:
            points_idx = [start_val, end_val]
        else:
            points_idx = [start_val]

        invisible_coord = coords[idx]

        # print("coords:", coords)
        # print("invisible_coord:", invisible_coord)

        for point_idx in points_idx:
            # print("visible_coord:", coords[point_idx])
            clip_plane = self.get_perspective_intersection_plane(
                coords[point_idx], invisible_coord
            )
            clip_plane = get_plane(clip_plane, [0, 0, 0])
            line_eqns = get_line_equations(invisible_coord, coords[point_idx])
            intersect_coords = plane_line_interesect(clip_plane, line_eqns)
            new_coords.append(intersect_coords)

        coords.pop(idx)

        for i in range(0, len(new_coords)):
            coords.insert(idx + i, new_coords[i])

        return coords

    def _get_visible_coords(self, coords, points_vis, angles_from_cp_normal):

        no_vertices = len(coords)
        if no_vertices > 2:
            lines = self._convert_shape_to_lines(coords, no_vertices)
        else:
            lines = coords

        for line in lines:
            self._get_plane_line_intersection(line, angles_from_cp_normal)

    def _convert_shape_to_lines(self, coords, no_vertices):
        lines = []
        for idx in range(coords):
            if idx == no_vertices - 1:
                next_idx = 0
            else:
                next_idx = idx + 1
            lines.append(coords[idx], coords[next_idx])
        return lines

    def _get_plane_line_intersection(self, line, angles):
        self.view_cone.plane_line_interesect(line, angles)

    def calc_light_colour(self, vector, face_normal, colour, intensity=1):
        """
        Calculates the colour of a surface given a light direction vector & base colour
        """
        light_dir_scale = math.sqrt(sum(vector))
        light_dir_normal = list(map(lambda c: c / light_dir_scale, vector))
        dot_prod = abs(sum(map(lambda a, b: a * b, face_normal, light_dir_normal))) ** 2
        colour = list(map(lambda a: self._light_colour(dot_prod, a, intensity), colour))

        return colour

    def _light_colour(self, dot_prod, value, intensity=1):
        colour = int(dot_prod * value * intensity)
        if colour > 255:
            colour = 255
        return colour

    def position_geometry(self, objs, position, angle=(0, 0, 0)):
        """
        transforms geometry of an object to it's "real" world coordinates given a position &
        angle coordinates
        """
        positioned_geometry = []
        for obj in objs:
            world_coords = []
            distances = []

            for coord in obj:
                coord = self.rotate.rotate_data(coord, angle)
                world_coord = sum_vectors(coord, position)
                distance = get_point_distance(self.camera_position, world_coord)
                distances.append(distance)
                world_coords.append(world_coord)

            average_distance = sum(distances) / len(distances)
            positioned_geometry.append(
                {"coords": world_coords, "distance": average_distance}
            )

        sorted_geometry = sorted(positioned_geometry, key=self._sort_by_distance)

        return sorted_geometry

    def _sort_by_distance(self, obj):
        return obj["distance"]

    def draw_object(self, geometry, position, angle=(0, 0, 0)):
        positioned_geometry = self.position_geometry(geometry, position, angle)
        perspective_geometry = self.convert_to_perspective(
            positioned_geometry, is_dict=True
        )

        for face_no in range(0, len(perspective_geometry)):
            face = perspective_geometry[face_no]
            face_3d = positioned_geometry[face_no]["coords"]
            vector_1 = sum_vectors(face_3d[1], face_3d[0], True)
            vector_2 = sum_vectors(face_3d[2], face_3d[0], True)
            normal = get_normal(vector_1, vector_2)
            colour = self.calc_light_colour(
                self.light_direction, normal, self.ship_base_colour
            )
            dir_vec_to_cam = sum_vectors(face_3d[0], self.camera_position, True)
            is_visible = vector_ang(normal, dir_vec_to_cam)

            if is_visible <= 90.0 and is_visible >= 0.0:
                self.draw_face(face, colour, 1, (0, 0, 0))

        return positioned_geometry, perspective_geometry

    def draw_face(self, face, colour, line_thickness=0, line_colour=None):
        pygame.draw.polygon(self.display_surface, colour, face, 0)
        if line_colour == None:
            line_colour = colour
        if line_thickness > 0:
            pygame.draw.polygon(self.display_surface, line_colour, face, line_thickness)

    def draw_lines(self, coords, colours=[], colour=None):
        len_colours = len(colours)
        for idx in range(0, len(coords)):
            # print(coord)
            if idx < len_colours:
                colour = colours[idx]
            print("line_colour:", colour)
            self.draw_line(coords[idx][0], coords[idx][1], colour)

    def draw_line(self, start_coords, end_coords, colour=None):
        if colour == None:
            colour = self.line_colour
        pygame.draw.aaline(self.display_surface, colour, start_coords, end_coords)

    def load_ship(self, filename, folder):
        # file_path = os.path.join(os.getcwd(), folder + filename)
        file_path = "/home/simon/python/flight-game/3d/ship/ship-geometry.json"
        with open(file_path, "r") as file:
            self.ship_data = json.load(file)
            file.close()
        faces = []
        booster_normal = (0.0, 0.0, 1.0)
        for face in self.ship_data["faces"]:
            rotated_face = []
            for vertex in face:
                rotated_face.append(
                    self.rotate.rotate_data(vertex, self.start_angle_ship)
                )
            faces.append(rotated_face)
        self.ship_data["faces"] = faces

        self.ship_data["booster"] = booster_normal
        self.ship_boost_vector = booster_normal
        self.ship_boost_vector_ang = [0.0, 0.0, 0.0]
        self.ship_dir_vector = self.ship_data["dir_vector"]

    def render_ship(self):
        if self.ship_start_pos[2] > 0.55:
            dv_dt = get_velocity_change([0.0, 0.0, 0.0], 1, self.time_rate)
            self.ship_velocity = sum_vectors(self.ship_velocity, dv_dt)
            dp = scale_vector(self.ship_velocity, self.time_rate)
            self.ship_start_pos = sum_vectors(self.ship_start_pos, dp)

        if self.ship_start_pos[2] < 0.5:
            self.ship_velocity = [0.0, 0.0, 0.0]
            self.ship_start_pos = sum_vectors(self.ship_start_pos, [0, 0, 0.5])

        self.hover_ship()

        # self.ship_data_positioned, _ = self.draw_object(
        #     self.ship_data["faces"], self.ship_start_pos, self.ship_angle
        # )

    def align_camera_to_ship(self):
        if self.align_cam_to_ship is True:
            dir_vector = self.rotate.rotate_data(self.ship_dir_vector, self.ship_angle)
            self.camera_position = sum_vectors(self.ship_start_pos, dir_vector)
            self.camera_ang = self.ship_angle
            self.rotate_camera([0, 0, self.cam_ang_rate])

    def rotate_ship(self, key):
        if key == K_LEFT:
            self._rotate_ship([0, 0, -self.ship_turn_rate])

        elif key == K_RIGHT:
            self._rotate_ship([0, 0, self.ship_turn_rate])

        elif key == K_UP:
            self._rotate_ship([-self.ship_turn_rate, 0, 0])

        elif key == K_DOWN:
            self._rotate_ship([self.ship_turn_rate, 0, 0])

        elif key == K_COMMA:
            self._rotate_ship([0, -self.ship_turn_rate, 0])

        elif key == K_PERIOD:
            self._rotate_ship([0, self.ship_turn_rate, 0])

    def _rotate_ship(self, angle_array):
        self.ship_angle = sum_vectors(self.ship_angle, angle_array)
        self.ship_boost_vector_ang = sum_vectors(
            self.ship_boost_vector_ang, angle_array
        )

    def boost_ship(self, amount):
        boost_vector = self.rotate.rotate_data(
            self.ship_boost_vector, self.ship_boost_vector_ang
        )
        boost_vec = scale_vector(boost_vector, amount)
        dv_dt = get_velocity_change(boost_vec, 1, self.time_rate)
        self.ship_velocity = sum_vectors(self.ship_velocity, dv_dt)
        dp = scale_vector(self.ship_velocity, self.time_rate)
        self.ship_start_pos = sum_vectors(self.ship_start_pos, dp)

    def hover_ship(self):
        if self.hover == True:
            amount = 9.81
            if self.ship_start_pos[2] < 50.0:
                if self.ship_velocity[2] < 0.0:
                    amount = 0.1 * abs(self.ship_velocity[2]) / self.time_rate + 19.5
            self.boost_ship(amount)

    def init_game(self):
        pygame.init()
        self.load_ship("ship-geometry.json", "3d/ship/")
        self.display_surface = pygame.display.set_mode(
            self.screen_dims, pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF, 32
        )

        # Set name in title bar
        pygame.display.set_caption("Flight Game")

        pygame.key.set_repeat(50, 10)

    def handle_events(self, events):
        for event in events:
            # print(event)
            if event.type == VIDEORESIZE:
                self.screen_dims = [event.w, event.h]
                # to reset the scale when resizing add scale var below
                self.display_surface = pygame.display.set_mode(
                    self.screen_dims, pygame.RESIZABLE | pygame.FULLSCREEN, 32
                )
                self.display_surface.fill(self.bkgrnd_colour)
                # Recalculate the maximum angle that an object is visible due to scren size change
                self.get_max_visible_angle()

            elif event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
                key = event.key
                if key == K_EQUALS:
                    if self.fov_ang < math.pi - 0.01:
                        self.fov_ang += math.pi / (self.fps * 20)
                elif key == K_MINUS:
                    if self.fov_ang > 0.01:
                        self.fov_ang -= math.pi / (self.fps * 20)

                elif key == K_l:
                    self.rotate_camera([0, 0, self.cam_ang_rate])
                elif key == K_r:
                    self.rotate_camera([0, 0, -self.cam_ang_rate])

                elif key == K_u:
                    self.rotate_camera([self.cam_ang_rate, 0, 0])

                elif key == K_d:
                    self.rotate_camera([-self.cam_ang_rate, 0, 0])

                elif key in [K_LEFT, K_RIGHT, K_UP, K_DOWN, K_COMMA, K_PERIOD]:
                    self.rotate_ship(key)

                elif key == K_RETURN:
                    self.boost_ship(30)

                elif key == K_h:
                    self.hover = True if self.hover == False else False

                elif key == K_a:
                    self.align_cam_to_ship = (
                        True if self.align_cam_to_ship == False else False
                    )

    def set_volumes(self, volumes):
        self.volumes = volumes

    # def draw_houses(self):
    #     no_houses = 5
    #     dist = 20
    #     colours = get_house_colours(self.volumes)
    #     for idx_x in range(-no_houses, no_houses):
    #         x = dist * idx_x
    #         for idx_y in range(-no_houses, no_houses):
    #             y = dist * idx_y
    #             house = draw_house(self.volumes, [x, y, 0])
    #             converted_house = self.convert_to_perspective(house)
    #             self.draw_lines(converted_house, colours)

    def create_grids(self):
        self.grids = []
        no_grids = 3
        dist = 20
        for idx_x in range(-no_grids, no_grids):
            x = dist * idx_x
            for idx_y in range(-no_grids, no_grids):
                y = dist * idx_y
                for idx_z in range(-no_grids, no_grids):
                    z = dist * idx_z
                    grid = Grid([x, y, z], self.fps, self.volumes)
                    self.grids.append(grid)
                    print("colours:", grid.get_colours())

    def draw_grids(self):
        if len(self.grids) != 0:
            for grid in self.grids:
                grid.update_grid(self.volumes)
                converted_grids = self.convert_to_perspective(grid.get_grid())
                # print("converted_grids", grid.get_grid())
                self.draw_lines(converted_grids, grid.get_colours())

    def main_loop(self, start_time):
        while True:
            try:
                self.display_surface.fill(self.bkgrnd_colour)
                self.align_camera_to_ship()

                # houses = threading.Thread(target=self.draw_houses)
                # houses.start()
                # self.draw_houses()

                self.draw_grids()

                converted_coords = self.convert_to_perspective(self.lines)
                self.draw_lines(converted_coords)
                self.handle_events(pygame.event.get())

                # Render ship
                self.render_ship()
                pygame.display.flip()
                self.fps_clock.tick(self.fps)
                end_time = time.time()
                self.counter += 1
                total_time = end_time - start_time
                # print("counter:", self.counter, "time:", total_time)
                # if self.counter > 30:
                #     break

            except Exception as error:
                print(error)
                print(traceback.format_exc())

                # Output data for debugging
                # with open("data.json", "w+") as file:
                #     json.dump(self.ship_data_positioned, file, indent=4)
                #     file.close()
                break
            # print("counter:", self.counter, "time:", total_time)

    def main(self):
        # Main game loop
        self.init_game()
        self.counter = 0
        start_time = time.time()

        x = threading.Thread(target=self.main_loop, args=(start_time,))
        x.start()


def create_test_data():
    lines = []

    # draw horizontal lines
    # no_y_lines = 10
    # dist_between = 2.0
    # for i in range(1, no_y_lines):
    #     # y = i - no_y_lines / 2 * dist_between
    #     y = i * dist_between
    #     lines.append([[-10.0, y, 0.0], [10.0, y, 0.0]])

    # draw lines along y plane
    no_x_lines = 2
    dist_between = 2.0
    for i in range(0, no_x_lines, 1):
        x = (i - no_x_lines / 2) * dist_between
        x = i
        # print(x)
        lines.append([[x, 10000.0, 0.0], [x, -10000.0, 0.0]])

    # # draw vertical lines randomly
    # for i in range(1, 100):
    #     x = (random.random() - 0.5) * 100
    #     y = (random.random() - 0.5) * 100
    #     z_1 = (random.random() - 0.5) * 2
    #     z_2 = z_1 + 1.0
    #     lines.append([[x, y, 0.0], [x, y, z_2]])

    # print(lines)

    return lines


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
