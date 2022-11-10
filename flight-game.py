import math, time

from ui.ui import *


def update_game(game):
    volumes = [1, 1, 1, 1, 1, 1, 1, 1]
    for i in range(0, 1000000):

        volumes[0] = math.cos(i * math.pi / 30)
        game.set_volumes(volumes)
        print("setting volume:", volumes[0])
        time.sleep(1 / 30)


if __name__ == "__main__":
    game = Game()
    # game.main()
    x = threading.Thread(target=game.main)
    x.start()
    print("exiting")
    # update_game(game)
