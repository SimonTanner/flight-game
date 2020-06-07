import pygame, sys, math, random, traceback, json, os
from pygame.locals import *

from physics.maths import *

class Game():
    def __init__(self, screen_dims=[1400, 900]):
        self.screen_dims = screen_dims
        self.fps = 30       # Frame rate
        self.fps_clock = pygame.time.Clock()
        self.bkgrnd_colour = (50, 50, 50)
        self.line_colour = (200, 50, 50)
        self.rotate = Rotate()

        # Camera constants
        self.camera_position = [0.0, -10.0, 06.0]
        self.fov_ang = math.pi / 2          # Field of View angle
        self.camera_ang = [0, 0, 0]         # angle between the z-axis and the centre of view  
        self.dist_clip_plane = 0.5          # Perpendicular distance from camera to clipping plane
        self.init_cp_normal = list(map(lambda coord: coord / self.dist_clip_plane, [0.0, self.dist_clip_plane, 0.0]))
        self.cp_normal = self.init_cp_normal
        self.init_perp_cp_vector()
        print(self.perp_vec_cp)
        self.get_clip_plane()

        self.light_direction = [1.0, 2.0, -1.0]

        # Consts for initialising ship
        self.start_angle_ship = [0.0, 0.0, 0.0]
        self.ship_angle = self.start_angle_ship
        self.ship_start_pos = [0.0, 20.0, 0.0]
        self.cam_ang_rate = math.pi / (self.fps * 5)

        self.lines = create_test_data()

    def init_perp_cp_vector(self):
        self.init_perp_vec_cp = self.rotate.rotate_data(self.init_cp_normal, (0, 0, math.pi/2))
        self.perp_vec_cp = self.init_perp_vec_cp

    def get_clip_plane(self):
        self.cp_centre_point = self.cp_normal
        self.blah_point = sum_vectors(self.cp_centre_point, self.perp_vec_cp)
        self.clip_plane = get_plane(self.cp_normal, self.blah_point)

    def rotate_camera(self, angle):
        """
        Rotates the camera and calculates the new clipping plane, it's normal and perpendicular vector
        """
        self.camera_ang = sum_vectors(self.camera_ang, angle)
        print(self.camera_ang)
        self.cp_normal = self.rotate.rotate_data(self.init_cp_normal, self.camera_ang)
        self.perp_vec_cp = self.rotate.rotate_data(self.init_perp_vec_cp, self.camera_ang)
        
        self.get_clip_plane()

    def convert_to_perspective(self, objs):
        # Calulate the scale required to translate between real coords & screen coords
        self.plane_height = math.tan(self.fov_ang / 2) * 2
        
        scr_scale = self.screen_dims[1] / self.plane_height
        print(scr_scale)
        # scr_scale = 10

        converted_coords = []

        for obj in objs:
            p = 1
            screen_coords = []
            print("--------------------------------------------------")
            for coord in obj:
                coords_to_point = [i - j for i, j in zip(coord, self.camera_position)]
                print(coords_to_point)

                is_inview = True if vector_ang(coords_to_point, self.cp_normal) < 90 else False

                if is_inview:
                    line_eqns = get_line_equations((0, 0, 0), coords_to_point)
                    # print("*****************************")
                    # print(line_eqns)
                    

                    intersect_coords = plane_line_interesect(self.clip_plane, line_eqns)
                    neg_cam_ang = list(map(lambda a: a * -1, self.camera_ang))
                    # print(intersect_coords)

                    rotated_coords = intersect_coords
                    # Get coords relative to camera centre point in the clipping plane
                    relative_coords = sum_vectors(intersect_coords, self.cp_centre_point, True)
                    # Rotate these back to get the values required in the 2d plane
                    plane_coords = self.rotate.unrotate_data(relative_coords, self.camera_ang)

                    print("*****************************")
                    
                    print(self.clip_plane)
                    print(line_eqns)
                    print(coords_to_point)
                    print(intersect_coords)
                    print(relative_coords)
                    print(plane_coords)
                    print("*****************************")

                    # rotated_coords = self.rotate.rotate_data(intersect_coords, neg_cam_ang)
                    delta_xy_in_vp = plane_coords[0]
                    delta_yz_in_vp = plane_coords[2]

                    scr_coord_x = round(self.screen_dims[0] / 2 - delta_xy_in_vp * scr_scale)
                    scr_coord_y = round(self.screen_dims[1] / 2 - delta_yz_in_vp * scr_scale)
                    
                    screen_coords.append([scr_coord_x, scr_coord_y])
                # print("---------------------------")
            # print(obj)
            print(screen_coords)

            if len(screen_coords) == 2:
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
                # print(face)
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

                # elif key == K_l:
                #     self.rotate_camera([0, -self.cam_ang_rate, 0])
                # elif key == K_r:
                #     self.rotate_camera([0, self.cam_ang_rate, 0])
                    
                elif key == K_u:
                    self.rotate_camera([self.cam_ang_rate, 0, 0])
                    
                elif key == K_d:
                    self.rotate_camera([-self.cam_ang_rate, 0, 0])

                elif key == K_LEFT:
                    self.rotate_camera([0, 0, self.cam_ang_rate])
                    # self.ship_angle = sum_vectors(self.ship_angle, [1, 0, 0])
                elif key == K_RIGHT:
                    self.rotate_camera([0, 0, -self.cam_ang_rate])
                    # self.ship_angle = sum_vectors(self.ship_angle, [-1, 0, 0])

                elif key == K_UP:
                    self.ship_angle = sum_vectors(self.ship_angle, [1, 0, 0])
                elif key == K_DOWN:
                    self.ship_angle = sum_vectors(self.ship_angle, [-1, 0, 0])
                


    def main(self):
        # Main game loop
        self.init_game()
        counter = 0
        while True:
            try:
                self.display_surface.fill(self.bkgrnd_colour)
                converted_coords = self.convert_to_perspective(self.lines)
                self.draw_lines(converted_coords)
                # print("----------------------------------")

                # Render ship
                # self.render_ship()
                
                # self.camera_ang = sum_vectors(self.camera_ang, [0, 0, -self.cam_ang_rate])

                self.handle_events(pygame.event.get())
                pygame.display.flip()
                self.fps_clock.tick(self.fps)
                counter += 1
                # sys.exit()
                # if counter == self.fps * 4:
                #     break

            except Exception as error:
                print(error)
                print(traceback.format_exc())

                # Output data for debugging
                # with open("data.json", "w+") as file:
                #     json.dump(self.ship_data_positioned, file, indent=4)
                #     file.close()
                break

def create_test_data():
    lines = []

    # # # draw horizontal lines
    no_y_lines = 10
    dist_between = 2.0
    for i in range(1, no_y_lines):
        # y = i - no_y_lines / 2 * dist_between
        y = i * dist_between
        lines.append([[-10.0, y, 0.0], [10.0, y, 0.0]])

    # # draw lines along y plane
    # no_x_lines = 100
    # dist_between = 2.0
    # for i in range(0, no_x_lines, 1):
    #     x = i - no_x_lines /2 * dist_between
    #     lines.append([[x , 10000000.0, 10.0], [x, 10.0, 10.0]])

    # # draw vertical lines randomly
    # for i in range(1, 100):
    #     x = (random.random() - 0.5) * 100
    #     y = (random.random() - 0.5) * 100
    #     z_1 = (random.random() - 0.5) * 2
    #     z_2 = z_1 + 1.0
    #     lines.append([[x, y, 0.0], [x, y, z_2]])

    # for i in range(0, 10):
    #     lines.append([[5.0, 5 + i, 0.0], [5.0, 5 + i, 6.0]])

    print(lines)

    return lines
