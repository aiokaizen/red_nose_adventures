import pygame
import sys
from settings import *
from level import Level
from tools import get_level_data


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    level = Level(get_level_data(1), screen)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        screen.fill('#000000')
        level.run()
        pygame.display.update()
        clock.tick(FPS)





