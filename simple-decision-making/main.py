import pygame
from game import Game
from constats import WIDTH, HEIGHT, FPS


def main():
    # dimensions (width, height)
    size = (WIDTH, HEIGHT)
    ground = pygame.display.set_mode(size)

    # Clock
    clock = pygame.time.Clock()

    # Caption
    pygame.display.set_caption("Let’s Play Soccer")

    # Start game
    game = Game(ground, clock)
    game.start()

    # On flag
    game_status = True
    while game_status:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_status = False

        game.next_frame()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
