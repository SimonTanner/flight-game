import pygame, sys

class Game():
    def __init__(self, screen_dims=[1400, 900]):
        self.screen_dims = screen_dims
        self.fps = 30
        self.fps_clock = pygame.time.Clock()
        self.bkgrnd_colour = (50, 50, 50)

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
            if event.type == VIDEORESIZE:
                self.screen_dims = [event.h, event.w]
                # to reset the scale when resizing add scale var below
                self.display_surface = pygame.display.set_mode(self.screen_dims, pygame.RESIZABLE | pygame.DOUBLEBUF, 32)
            if event.type == QUIT:
                sys.exit()


    def main(self):
        # Main game loop
        self.init_game()
        while True:
            try:
                self.display_surface.fill(self.bkgrnd_colour)
                self.handle_events(pygame.event.get())
                pygame.display.flip()
                self.fps_clock.tick(self.fps)
            except Exception:
                break
