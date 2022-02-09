import pygame
import sys
from settings import *
from level import Level

from game import Game


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    game  = Game(screen)

    while True:
        for event in pygame.event.get(pygame.QUIT):
            pygame.quit()
            sys.exit()
        
        screen.fill('#000000')
        
        game.run()
        
        pygame.display.update()
        clock.tick(FPS)





