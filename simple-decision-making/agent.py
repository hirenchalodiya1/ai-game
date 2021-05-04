import pygame
import random
from sympy import Point, Circle
from constats import INNER_BOX, OUTER_BOX, PLAYER_RADIUS, WIDTH, HEIGHT


class Positions:
    used = set()

    @staticmethod
    def _check(cx, cy):
        p = Point(cx, cy)
        for x, y in Positions.used:
            if p.distance((x, y)) <= 2 * PLAYER_RADIUS:
                return False
        else:
            Positions.used.add((cx, cy))
            return True

    @staticmethod
    def get_inner_box():
        pos_x = random.randint(INNER_BOX.LEFT, INNER_BOX.RIGHT)
        pos_y = random.randint(INNER_BOX.UP, INNER_BOX.DOWN)

        if not Positions._check(pos_x, pos_y):
            return Positions.get_inner_box()
        else:
            return pos_x, pos_y

    @staticmethod
    def get_outer_box():
        pos_x = random.randint(OUTER_BOX.LEFT, OUTER_BOX.RIGHT)
        pos_y = random.randint(OUTER_BOX.UP, OUTER_BOX.DOWN)

        if not Positions._check(pos_x, pos_y):
            return Positions.get_outer_box()
        else:
            return pos_x, pos_y

    @staticmethod
    def get_specific(x, y):
        Positions.used.add((x, y))
        return x, y


class Player(pygame.sprite.Sprite):
    team = None
    radius = PLAYER_RADIUS
    color = None
    point = None
    circle = None
    vector = None
    number = None

    def __init__(self, position, color, number, *groups):
        super().__init__(*groups)
        self.point = Point(position[0], position[1])
        self.circle = Circle(self.point, self.radius)
        self.vector = pygame.math.Vector2()
        self.vector.x = position[0]
        self.vector.y = position[1]
        self.color = color
        self.number = number

        self.image = pygame.Surface([WIDTH, HEIGHT], pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, position, self.radius)

        self.rect = self.image.get_rect()

    def __str__(self):
        return f"<Player ({self.vector.x}, {self.vector.y} | Number {self.number})>"

    def __repr__(self):
        return f"{self.number} "


class Team(pygame.sprite.Group):
    NUMBER = None
    team_name = None

    def __init__(self, *sprites):
        super(Team, self).__init__(sprites)
        if hasattr(self, 'init') and callable(self.init):
            self.init()

    def __str__(self):
        return f"<{self.team_name} Team: {self.NUMBER}>"

    def __repr__(self):
        return self.__str__()


class RedTeam(Team):
    NUMBER = 3
    team_name = "Red"
    color = "red"

    def init(self):
        if self.NUMBER < 2:
            raise ValueError("Red team should have at-least 2 member")

        # For testing purpose
        # self.add(Player(Positions.get_specific(183, 62), self.color, 1))
        # self.add(Player(Positions.get_specific(500, 263), self.color, 2))
        # self.add(Player(Positions.get_specific(491, 205), self.color, 3))

        # put at least one player in inner box
        self.add(Player(Positions.get_inner_box(), self.color, 1))

        for i in range(self.NUMBER - 1):
            self.add(Player(Positions.get_outer_box(), self.color, i + 2))


class BlueTeam(Team):
    NUMBER = 4
    team_name = "Blue"
    color = "blue"
    center_player = None

    def init(self):
        if self.NUMBER < 3:
            raise ValueError("Blue team should have at-least 3 member")

        # Put player in center
        t = OUTER_BOX.DOWN + PLAYER_RADIUS
        self.center_player = Player(Positions.get_specific(OUTER_BOX.CENTER_X, t), self.color, 1)
        self.add(self.center_player)

        # For testing purpose
        # self.add(Player(Positions.get_specific(109, 54), self.color, 2))
        # self.add(Player(Positions.get_specific(177, 271), self.color, 3))
        # self.add(Player(Positions.get_specific(508, 277), self.color, 4))

        # put second player in inner box
        self.add(Player(Positions.get_inner_box(), self.color, 2))

        for i in range(self.NUMBER - 2):
            self.add(Player(Positions.get_outer_box(), self.color, i + 3))
