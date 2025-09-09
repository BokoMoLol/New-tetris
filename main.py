import pygame
from game import Game

def main():
    pygame.init()
    screen = pygame.display.set_mode((570, 600))  # 120 + 300 + 150
    pygame.display.set_caption("Tetris")
    
    game = Game(screen)
    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()