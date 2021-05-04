from enum import Enum
import pygame
import math
from sympy import intersection, Segment, Point
from agent import RedTeam, BlueTeam
from ball import Ball
from constats import OUTER_BOX, PLAYER_RADIUS, GOAL_POST, WIDTH, HEIGHT, FPS
from utils import shortest_n_paths


def merge_segments(segments):
    if len(segments) < 2:
        return segments
    ret = []
    prev_x, prev_y = segments[0]
    for x, y in segments[1:]:
        if prev_y < x - 1:
            # x starts new segment
            ret.append((prev_x, prev_y))
            prev_x, prev_y = x, y
        else:
            prev_y = max(y, prev_y)
    ret.append((prev_x, prev_y))
    return ret


def get_path(x1, x2, y1, y2):
    speed = 2
    ret = []
    if x1 == x2:
        iterable = range(y1, y2 + 1, speed) if y2 > y1 else range(y1, y2 - 1, -speed)
        for i in iterable:
            ret.append((x1, i))
        return ret

    slope = (y1 - y2) / (x1 - x2)
    c = y1 - ((y1 - y2) * x1 / (x1 - x2))

    if abs(slope) < 1:
        iterable = range(x1, x2 + 1, speed) if x2 > x1 else range(x1, x2 - 1, -speed)
        for x in iterable:
            y = int(slope * x + c)
            ret.append((x, y))
        return ret
    else:
        iterable = range(y1, y2 + 1, speed) if y2 > y1 else range(y1, y2 - 1, -speed)
        for y in iterable:
            x = int((y - c) / slope)
            ret.append((x, y))
        return ret


class GameState:
    blue_team = None
    red_team = None
    kicker = None

    ball_reachable = None
    sight = {}
    direct_shoot = {}
    tangents = []

    def __init__(self, blue_team, red_team, kicker):
        self.blue_team = blue_team
        self.red_team = red_team
        self.kicker = kicker
        self.ball_reachable = {self.blue_team.center_player: False}

    def calculate_sight(self):
        self._calculate_sight(self.kicker)

        for p in self.blue_team.sprites():
            self._calculate_shoot(p)

    def _calculate_sight(self, player):
        # If it already been checked then end recursion
        if self.ball_reachable[player]:
            return
        # Make player flag True
        self.ball_reachable[player] = True

        player_group = player.groups()[0]
        # for each player in the group
        for p in player_group.sprites():

            # if it's not same player then check sight
            if p != player and self._check_sight(player, p):
                # add player to sight
                if player in self.sight:
                    self.sight[player].add(p)
                else:
                    self.sight[player] = {p}
                # self.sight[player] = self.sight.get(player, set()).add(p)

                # if there is clean sight and it is not added in ball reachable then add it
                if p not in self.ball_reachable:
                    self.ball_reachable[p] = False
                # calculate sight for p
                self._calculate_sight(p)

    def _check_sight(self, p1, p2):
        for opposite_p in self.red_team.sprites():
            if intersection(Segment(p1.point, p2.point), opposite_p.circle):
                return False
        else:
            return True

    def _calculate_shoot(self, player):
        removable_segment = list()
        for p in self.red_team.sprites():
            if p.vector.y + PLAYER_RADIUS >= player.vector.y:
                # Just ignore them
                continue
            t1, t2 = p.circle.tangent_lines(player.point)
            y = GOAL_POST.Y
            c1 = t1.coefficients
            c2 = t2.coefficients

            x1 = (c1[1] * y + c1[2]) / (-c1[0]) if c1[0] != 0 else y
            x2 = (c2[1] * y + c2[2]) / (-c2[0]) if c2[0] != 0 else y

            x1, x2 = (x1, x2) if x1 < x2 else (x2, x1)
            removable_segment.append((math.floor(x1), math.ceil(x2)))

            # add for illustration purpose
            self.tangents.append((player.point, (x1, GOAL_POST.Y)))
            self.tangents.append((player.point, (x2, GOAL_POST.Y)))

        removable_segment.sort(key=lambda k: k[0])
        removable_segment = merge_segments(removable_segment)

        left_covered = False
        right_covered = False
        point_x_covered = not GOAL_POST.LEFT <= player.vector.x <= GOAL_POST.RIGHT
        min_point = None
        min_cost = float('inf')

        for x, y in removable_segment:
            if not left_covered and x <= GOAL_POST.LEFT <= y:
                left_covered = True
            if not right_covered and x <= GOAL_POST.RIGHT <= y:
                right_covered = True
            if not point_x_covered and x <= player.vector.x <= y:
                point_x_covered = True

            if GOAL_POST.LEFT <= x <= GOAL_POST.RIGHT:
                cost = player.point.distance((x, GOAL_POST.Y))
                if cost < min_cost:
                    min_cost = cost
                    min_point = Point(x, GOAL_POST.Y)

            if GOAL_POST.LEFT <= y <= GOAL_POST.RIGHT:
                cost = player.point.distance((y, GOAL_POST.Y))
                if cost < min_cost:
                    min_cost = cost
                    min_point = Point(y, GOAL_POST.Y)

        if not left_covered:
            cost = player.point.distance((GOAL_POST.LEFT, GOAL_POST.Y))
            if cost < min_cost:
                min_cost = cost
                min_point = Point(GOAL_POST.LEFT, GOAL_POST.Y)

        if not right_covered:
            cost = player.point.distance((GOAL_POST.RIGHT, GOAL_POST.Y))
            if cost < min_cost:
                min_cost = cost
                min_point = Point(GOAL_POST.RIGHT, GOAL_POST.Y)

        if not point_x_covered:
            cost = player.point.distance((player.vector.x, GOAL_POST.Y))
            if cost < min_cost:
                # min_cost = cost
                min_point = Point(player.vector.x, GOAL_POST.Y)

        if min_point:
            self.direct_shoot[player] = min_point

    def find_path(self):
        paths = shortest_n_paths(self.kicker, self.sight, self.direct_shoot, 2)
        if len(paths) == 0:
            raise Exception("Agent could not found path")

        print("Best possible paths are, with heuristic costs")
        for p in paths:
            print(f"{p}, cost = {float(p.cost)}")
        return paths[0]


class GameDisplayState(Enum):
    TANGENTS = 1
    SHOOTS_AVAILABLE = 2
    SHOOT = 3


class Game:
    screen = None
    clock = None
    red_team = None
    blue_team = None
    ball = None
    state = None
    optimal_path = []
    path_frame_counter = 0
    display_state = GameDisplayState.TANGENTS

    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock

        self.blue_team = BlueTeam()
        self.red_team = RedTeam()
        self.ball = Ball((OUTER_BOX.CENTER_X, OUTER_BOX.DOWN + PLAYER_RADIUS))
        self.ball_surface = pygame.sprite.Group()
        self.ball_surface.add(self.ball)

        self.state = GameState(self.blue_team, self.red_team, self.blue_team.center_player)

    def print_player_info(self):
        # spawn read team
        print("Spawning Red Team...")
        for p in self.red_team.sprites():
            print(f"\t{p}")

        # spawn blue team
        print("Spawning Blue Team...")
        for p in self.blue_team.sprites():
            print(f"\t{p}")

    def spawn_player(self):
        self.red_team.draw(self.screen)
        self.blue_team.draw(self.screen)
        pygame.display.update()

    def display_ground(self):
        # Background image
        bg = pygame.image.load('bg.png').convert()
        self.screen.blit(bg, [0, 0])
        pygame.display.flip()

    def clear(self):
        self.display_ground()
        self.spawn_player()

    def render_path(self, path):
        points = []
        for i in path.path[:-1]:
            points.append(i.point)
        points.append(path.path[-1])

        for p1, p2 in zip(points, points[1:]):
            self.optimal_path += get_path(p1.x, p2.x, p1.y, p2.y)

    def pre_process(self):
        print("All agents deciding shots...")
        self.state.calculate_sight()
        print("Kicker finding optimal path...")
        path_point = self.state.find_path()

        self.render_path(path_point)

    def start(self):
        pygame.init()
        self.display_ground()
        self.print_player_info()
        self.spawn_player()
        print()
        print("Game Started")
        self.pre_process()

    def show_tangents(self):
        # show tangents for first time then do not change display
        if self.path_frame_counter == 0:
            print("Showing agent's decision making...")
            self.clear()
            tangent_surface = pygame.Surface([WIDTH, HEIGHT], pygame.SRCALPHA)
            for t in self.state.tangents:
                pygame.draw.line(tangent_surface, 'white', t[0], t[1])
            self.screen.blit(tangent_surface, [0, 0])
            pygame.display.update()

        if self.path_frame_counter < 2 * FPS:
            self.path_frame_counter += 1
        else:
            # renew counter and change state
            self.path_frame_counter = 0
            self.display_state = GameDisplayState.SHOOTS_AVAILABLE

    def show_shots(self):
        # show shots for first time then do not change display
        if self.path_frame_counter == 0:
            print("Showing shots selected by agent...")
            self.clear()
            shots_surface = pygame.Surface([WIDTH, HEIGHT], pygame.SRCALPHA)

            # showing passing
            for p1, p_set in self.state.sight.items():
                for p2 in p_set:
                    pygame.draw.line(shots_surface, 'pink', p1.vector, p2.vector)

            # # showing direct shoots
            for p1, point in self.state.direct_shoot.items():
                pygame.draw.line(shots_surface, 'pink', p1.vector, point)

            self.screen.blit(shots_surface, [0, 0])
            pygame.display.update()

        if self.path_frame_counter < 2 * FPS:
            self.path_frame_counter += 1
        else:
            # renew counter and change state
            self.path_frame_counter = 0
            self.display_state = GameDisplayState.SHOOT

    def shoot(self):
        if self.path_frame_counter == 0:
            print("Rendering path...")

        # update ball position till we have
        if self.path_frame_counter < len(self.optimal_path):
            self.clear()
            position = self.optimal_path[self.path_frame_counter]
            self.ball.update(*position)
            self.path_frame_counter += 1
            # showing on screen
            self.ball_surface.draw(self.screen)
        else:
            self.clock.tick(2)
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def next_frame(self):
        if self.display_state == GameDisplayState.TANGENTS:
            self.show_tangents()
        elif self.display_state == GameDisplayState.SHOOTS_AVAILABLE:
            self.show_shots()
        elif self.display_state == GameDisplayState.SHOOT:
            self.shoot()
        else:
            raise ValueError("Unknown display state")
