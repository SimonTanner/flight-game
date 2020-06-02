import pygame, sys, math
from pygame.locals import *

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
        for i in range(1, 100):
            self.lines.append([float(i), 0.0, 0.0])

    def generate_perspective(self):
        self.plane_height = self.dist_clip_plane * math.tan(self.fov_ang / 2) * 2
        scr_scale = self.plane_height / self.screen_dims[0]
        dist_view_edge = self.view_height * math.tan(self.view_ang_delta)

        for line in self.lines:
            dist_to_cam = line[0]
            real_height = line[2]
            if self.view_height != real_height:
                ang_to_point = self.view_ang - math.atan(
                    (dist_view_edge + dist_to_cam) / (self.view_height - real_height)
                )
            else:
                ang_to_point = 0
            height_in_vp = self.dist_clip_plane * math.tan(ang_to_point)

            
            scr_height_from_centre = height_in_vp / scr_scale
            height = round(self.screen_dims[1] / 2 + scr_height_from_centre)
            
            self.draw_line([0, height], [self.screen_dims[0], height])

            # print('line: ' + str(line[0]) + ', angle: ' + str(ang_to_point) + ', height vp: ' + str(height_in_vp) + ', scale: ' + str(scr_scale))
            # print(height)

    def draw_line(self, start_coords, end_coords):
        pygame.draw.line(self.display_surface, self.line_colour, start_coords, end_coords)
            

    def init_game(self):
        pygame.init()

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
                self.display_surface = pygame.display.set_mode(self.screen_dims, pygame.RESIZABLE | pygame.DOUBLEBUF, 32)
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

                elif key == K_UP:
                    self.view_ang += math.pi / (self.fps * 20)
                elif key == K_DOWN:
                    self.view_ang -= math.pi / (self.fps * 20)


    def main(self):
        # Main game loop
        self.init_game()
        while True:
            try:
                # self.view_height += 1.0 / self.fps
                # self.view_ang += math.pi / (20 * self.fps)
                self.display_surface.fill(self.bkgrnd_colour)
                self.generate_perspective()
                self.handle_events(pygame.event.get())
                pygame.display.flip()
                self.fps_clock.tick(self.fps)
            except Exception as error:
                print(error)
                break
