import pygame
import sys
from settings import *
from tools import debug

from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Red nose adventures")
    clock = pygame.time.Clock()
    game  = Game(screen)

    while True:
        for _ in pygame.event.get(pygame.QUIT):
            pygame.quit()
            sys.exit()
        
        game.run()

        if DEBUG:
            debug_infos = 'DEBUG mode is ON...'
            debug(debug_infos, screen)
        
        pygame.display.update()
        debug.reset()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
