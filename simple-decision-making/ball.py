import pygame
from constats import BALL_RADIUS


class Ball(pygame.sprite.Sprite):
    radius = BALL_RADIUS
    color = "black"

    def __init__(self, position, *groups):
        super().__init__(*groups)
        self.position = position

        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()

    def update(self, x, y):
        self.rect.x = x - self.radius
        self.rect.y = y - self.radius
