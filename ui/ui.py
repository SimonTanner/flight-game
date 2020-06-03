import pygame, sys, math, random, traceback, json, os
from pygame.locals import *

from physics.physics import *

class Game():
    def __init__(self, screen_dims=[1400, 900]):
        self.screen_dims = screen_dims
        self.fps = 30
        self.fps_clock = pygame.time.Clock()
        self.bkgrnd_colour = (50, 50, 50)
        self.line_colour = (200, 50, 50)
        # self.view_cntr_ang = math.pi / 2
        self.fov_ang = math.pi / 3      # Field of View angle
        self.view_ang = math.pi / 2     # angle between the z-axis and the centre of view
        self.view_ang_delta = self.view_ang - self.fov_ang / 2   
        self.view_height = 2.0
        self.dist_clip_plane = 1.0
        self.lines = []
        self.light_direction = [1.0, 2.0, -1.0]
        self.start_angle_ship = [0.0, 0.0, 0.0]
        self.ship_angle = self.start_angle_ship
        self.ship_start_pos = [10.0, 0.0, 0.0]
        self.rotate = Rotate()
        self.create_test_data()

    def create_test_data(self):
        for i in range(1, 100):
            self.lines.append([[float(i), -5.0, 0.0], [float(i), 10.0, 0.0]])
        for i in range(1, 100):
            self.lines.append([[1.0, 50-float(i), 0.0], [500.0, 50-float(i), 0.0]])
        for i in range(1, 100):
            x = (random.random() - 0.5) * 100
            y = (random.random() - 0.5) * 100
            z_1 = (random.random() - 0.5) * 10
            z_2 = z_1 + 1.0
            self.lines.append([[x, y, z_1], [x, y, z_2]])
        

    def convert_to_perspective(self, objs):
        self.plane_height = self.dist_clip_plane * math.tan(self.fov_ang / 2) * 2
        scr_scale = self.screen_dims[0] / self.plane_height
        dist_view_edge = self.view_height * math.tan(self.view_ang_delta)
        horizontal_ang = math.atan(self.screen_dims[1] / (2* scr_scale * self.dist_clip_plane))

        converted_coords = []

        for obj in objs:
            screen_coords = []
            for coord in obj:
                dist_to_cam = coord[0]
                real_y = coord[1]
                real_height = coord[2]
                if self.view_height != real_height:
                    ang_to_point_xz = self.view_ang - math.atan(
                        (dist_view_edge + dist_to_cam) / (self.view_height - real_height)
                    )
                else:
                    ang_to_point_xz = 0
                
                height_in_vp = self.dist_clip_plane * math.tan(ang_to_point_xz)
                ang_to_point_yx = math.atan(real_y / (dist_to_cam))
                width_in_vp = self.dist_clip_plane * math.tan(ang_to_point_yx)

                
                scr_height_from_centre = height_in_vp * scr_scale
                height = round(self.screen_dims[1] / 2 + scr_height_from_centre)

                scr_width_from_centre = width_in_vp * scr_scale
                width = round(self.screen_dims[0] / 2 + scr_width_from_centre)
                screen_coords.append([width, height])

            # print('line: ' + str(line[0]) + ', angle: ' + str(ang_to_point_xz) + ', height vp: ' + str(height_in_vp) + ', scale: ' + str(scr_scale))
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
        updated_geometry = []
        for obj in objs:
            world_coords = []
            for coord in obj:
                print(angle)
                print(coord)
                coord = self.rotate.rotate_data(coord, angle)
                print(coord)
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
            print(face_no)
            normal = get_normal(vector_1, vector_2)
            colour = self.calc_light_colour(self.light_direction, normal, base_colour)
            is_visible = dot_product(normal, [1, 0, 0])
            if is_visible[0] >= 0.0:
                self.draw_face(perspective_geometry[face_no], colour)

        return positioned_geometry, perspective_geometry

    def draw_face(self, face, colour):
        pygame.draw.polygon(self.display_surface, colour, face, 0)

    def draw_lines(self, coords):
        for coord in coords:
            self.draw_line(coord[0], coord[1])

    def draw_line(self, start_coords, end_coords):
        pygame.draw.line(self.display_surface, self.line_colour, start_coords, end_coords)

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

                # elif key == K_UP:
                #     self.view_ang += math.pi / (self.fps * 20)
                # elif key == K_DOWN:
                #     self.view_ang -= math.pi / (self.fps * 20)

                elif key == K_UP:
                    self.ship_angle = sum_vectors(self.ship_angle, [0, 1, 0])
                elif key == K_DOWN:
                    self.ship_angle = sum_vectors(self.ship_angle, [0, -1, 0])
                elif key == K_LEFT:
                    self.ship_angle = sum_vectors(self.ship_angle, [1, 0, 0])
                elif key == K_RIGHT:
                    self.ship_angle = sum_vectors(self.ship_angle, [-1, 0, 0])


    def main(self):
        # Main game loop
        self.init_game()
        while True:
            try:
                # self.view_height += 1.0 / self.fps
                # self.view_ang += math.pi / (20 * self.fps)
                self.display_surface.fill(self.bkgrnd_colour)
                converted_coords = self.convert_to_perspective(self.lines)
                self.draw_lines(converted_coords)
                # Render ship
                self.render_ship()
                self.handle_events(pygame.event.get())
                pygame.display.flip()
                self.fps_clock.tick(self.fps)

            except Exception as error:
                print(error)
                print(traceback.format_exc())

                # Output data for debugging
                with open("data.json", "w+") as file:
                    json.dump(self.ship_data_positioned, file, indent=4)
                    file.close()
                break
