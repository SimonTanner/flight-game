import pygame, sys, math, random, traceback, json, os
from pygame.locals import *

from physics.maths import *

class Game():
    def __init__(self, screen_dims=[1400, 900]):
        self.screen_dims = screen_dims
        self.fps = 30
        self.fps_clock = pygame.time.Clock()
        self.bkgrnd_colour = (50, 50, 50)
        self.line_colour = (200, 50, 50)

        # Camera constants
        self.camera_position = [0.0, 0.0, 2.0]
        self.fov_ang = math.pi / 3          # Field of View angle
        self.camera_ang = [0, 0, 0]       # angle between the z-axis and the centre of view  
        self.dist_clip_plane = 1.0          # Perpendicular distance from camera to clipping plane

        self.light_direction = [1.0, 2.0, -1.0]

        # Consts for initialising ship
        self.start_angle_ship = [0.0, 0.0, 0.0]
        self.ship_angle = self.start_angle_ship
        self.ship_start_pos = [10.0, 0.0, 0.0]

        self.rotate = Rotate()
        self.create_test_data()

    def create_test_data(self):
        # draw horizontal lines
        self.lines = []
        for i in range(1, 1000):
            self.lines.append([[-10.0, float(i), 0.0], [10.0, float(i), 0.0]])

        # # draw lines along y plane
        # no_x_lines = 100
        # for i in range(0, no_x_lines):
        #     x = i - no_x_lines / 2
        #     self.lines.append([[x , 10000000.0, 0.0], [x, .01, 0.0]])

        # draw vertical lines randomly
        for i in range(1, 100):
            x = (random.random() - 0.5) * 100
            y = (random.random() - 0.5) * 100
            z_1 = (random.random() - 0.5) * 2
            z_2 = z_1 + 1.0
            self.lines.append([[x, y, z_1], [x, y, z_2]])
        

    def convert_to_perspective(self, objs):
        # Calulate the scale required to translate between real coords & screen coords
        self.plane_height = self.dist_clip_plane * math.tan(self.fov_ang / 2) * 2
        scr_scale = self.screen_dims[1] / self.plane_height

        converted_coords = []

        for obj in objs:
            screen_coords = []
            for coord in obj:
                dist_x, dist_y, dist_z = [i - j for i, j in zip(coord, self.camera_position)]
                # print(dist_x, dist_y, dist_z)
                camera_ang = list(map(lambda a: math.degrees(a), self.camera_ang))
                dist_x, dist_y, dist_z = self.rotate.rotate_data((dist_x, dist_y, dist_z), camera_ang)
                # Calculate the angle to the object between the camera in the yz (vertical) &
                # xy (horizontal) planes
                if dist_y == 0.0:
                    # if dist_y == 0 there will be division by zero error
                    dist_y = 0.00001

                ang_to_point_yz = math.atan(
                    dist_z / dist_y
                )
                ang_to_point_xy = math.atan(
                    dist_x / dist_y
                )
                # else:
                #     # ang_to_point_yz = 0
                #     # ang_to_point_xy = 0
                #     ang_to_point_yz = math.pi / 2
                #     ang_to_point_xy = math.pi / 2

                delta_xy_in_vp = self.dist_clip_plane * math.tan(ang_to_point_xy) # + self.camera_ang[0]) 
                delta_yz_in_vp = self.dist_clip_plane * math.tan(ang_to_point_yz) # + self.camera_ang[1]) #* (1 - math.sin(ang_to_point_xy) * math.cos(self.camera_ang[0]))

                scr_coord_y = round(self.screen_dims[1] / 2 - delta_yz_in_vp * scr_scale)
                scr_coord_x = round(self.screen_dims[0] / 2 - delta_xy_in_vp * scr_scale)
                
                screen_coords.append([scr_coord_x, scr_coord_y])

            # print(screen_coords)
            # print('line: ' + str(line[0]) + ', angle: ' + str(ang_to_point_yz) + ', height vp: ' + str(height_in_vp) + ', scale: ' + str(scr_scale))
            # print(height)
            converted_coords.append(screen_coords)
        # print(converted_coords)
        # sys.exit()
        return converted_coords

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
        updated_geometry = []
        for obj in objs:
            world_coords = []
            for coord in obj:
                # print(angle)
                # print(coord)
                coord = self.rotate.rotate_data(coord, angle)
                # print(coord)
                world_coord = sum_vectors(coord, position)
                world_coords.append(world_coord)
            updated_geometry.append(world_coords)
        return updated_geometry

    def draw_object(self, geometry, position, angle=(0, 0, 0)):
        positioned_geometry = self.position_geometry(geometry, position, angle)
        perspective_geometry = self.convert_to_perspective(positioned_geometry)

        for face_no in range(0, len(perspective_geometry)):
            face = perspective_geometry[face_no]
            base_colour = (200, 50, 150)
            face_3d = positioned_geometry[face_no]
            vector_1 = sum_vectors(face_3d[1], face_3d[0], True)
            vector_2 = sum_vectors(face_3d[2], face_3d[1], True)
            # print(face_no)
            normal = get_normal(vector_1, vector_2)
            colour = self.calc_light_colour(self.light_direction, normal, base_colour)
            is_visible = dot_product(normal, [1, 0, 0])
            if is_visible[0] >= 0.0:
                print(face)
                self.draw_face(face, colour, 1, (0, 0, 0))

        return positioned_geometry, perspective_geometry

    def draw_face(self, face, colour, line_thickness=0, line_colour=None):
        pygame.draw.polygon(self.display_surface, colour, face, 0)
        if line_colour == None:
            line_colour = colour
        if line_thickness > 0:
            pygame.draw.polygon(self.display_surface, line_colour, face, line_thickness)

    def draw_lines(self, coords, colour=None):
        for coord in coords:
            # print(coord)
            self.draw_line(coord[0], coord[1], colour)

    def draw_line(self, start_coords, end_coords, colour=None):
        if colour == None:
            colour = self.line_colour
        pygame.draw.line(self.display_surface, colour, start_coords, end_coords)

    def load_ship(self, filename, folder):
        # "/".join(os.getcwd().split("/")[0:-1])
        file_path = os.path.join(os.getcwd(), folder + filename)
        with open(file_path, "r") as file:
            self.ship_data = json.load(file)
            file.close()

    def render_ship(self):
        print(self.ship_angle)
        self.ship_data_positioned, _ = self.draw_object(
            self.ship_data['faces'], self.ship_start_pos, self.ship_angle
        )
            

    def init_game(self):
        pygame.init()
        self.load_ship("ship-geometry.json", "3d/ship/")

        # Load icon
        # logo_rel_path = 'logo/Bio-Logo-v1.jpg'
        # logo_path = os.path.join(os.getcwd(), logo_rel_path)
        # logo = pygame.image.load(logo_path)
        # pygame.display.set_icon(logo)


        self.display_surface = pygame.display.set_mode(
            self.screen_dims,
            pygame.RESIZABLE|pygame.HWSURFACE|pygame.DOUBLEBUF,
            32
        )

        # Set name in title bar
        pygame.display.set_caption('Flight Game')
        
        pygame.key.set_repeat(50, 10)

    def handle_events(self, events):
        for event in events:
            # print(event)
            if event.type == VIDEORESIZE:
                self.screen_dims = [event.w, event.h]
                # to reset the scale when resizing add scale var below
                self.display_surface = pygame.display.set_mode(
                    self.screen_dims, pygame.RESIZABLE | pygame.DOUBLEBUF, 32
                )
                self.display_surface.fill(self.bkgrnd_colour)

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
                    self.camera_ang = sum_vectors(self.camera_ang, [-math.pi / (self.fps * 20), 0, 0])
                elif key == K_r:
                    self.camera_ang = sum_vectors(self.camera_ang, [math.pi / (self.fps * 20), 0, 0])
                elif key == K_u:
                    self.camera_ang = sum_vectors(self.camera_ang, [0, -math.pi / (self.fps * 20), 0])
                elif key == K_d:
                    self.camera_ang = sum_vectors(self.camera_ang, [0, math.pi / (self.fps * 20), 0])

                elif key == K_UP:
                    self.ship_angle = sum_vectors(self.ship_angle, [0, 1, 0])
                elif key == K_DOWN:
                    self.ship_angle = sum_vectors(self.ship_angle, [0, -1, 0])
                elif key == K_LEFT:
                    self.camera_ang = sum_vectors(self.camera_ang, [0, 0, math.pi / (self.fps * 20)])
                    # self.ship_angle = sum_vectors(self.ship_angle, [1, 0, 0])
                elif key == K_RIGHT:
                    self.camera_ang = sum_vectors(self.camera_ang, [0, 0, -math.pi / (self.fps * 20)])
                    # self.ship_angle = sum_vectors(self.ship_angle, [-1, 0, 0])


    def main(self):
        # Main game loop
        self.init_game()
        while True:
            try:
                self.display_surface.fill(self.bkgrnd_colour)
                converted_coords = self.convert_to_perspective(self.lines)
                self.draw_lines(converted_coords)
                print(self.camera_ang)
                # Render ship
                # self.render_ship()
                self.handle_events(pygame.event.get())
                pygame.display.flip()
                self.fps_clock.tick(self.fps)

            except Exception as error:
                print(error)
                print(traceback.format_exc())

                # Output data for debugging
                # with open("data.json", "w+") as file:
                #     json.dump(self.ship_data_positioned, file, indent=4)
                #     file.close()
                break
