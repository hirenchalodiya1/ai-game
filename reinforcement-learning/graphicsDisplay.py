from graphicsUtils import *
import math
import time
import os
from game import Directions

###########################
#  GRAPHICS DISPLAY CODE  #
###########################

# Most code by Dan Klein and John Denero written
# Some code from a by LiveWires, and used / modified with permission.

DEFAULT_GRID_SIZE = 50.0
BACKGROUND_COLOR = formatColor(1, 1, 1)

# info pane
INFO_PANE_HEIGHT = 35
SCORE_COLOR = formatColor(1, 1, 1)

# agent
AGENT_OUTLINE_WIDTH = 2
AGENT_COLOR = formatColor(111.0 / 255.0, 168.0 / 255.0, 220.0 / 255)
AGENT_SCALE = 0.5

# Drawing walls
WALL_COLOR = formatColor(0.0 / 255.0, 51.0 / 255.0, 255.0 / 255.0)
WALL_RADIUS = 0.15

# Go to power position
GO_TO_POWER_COLOR = formatColor(0, 1, 0)
GO_TO_POWER_SCALE = 0.5
GO_TO_POWER_SHAPE = [(-0.75, -0.75), (0.75, -0.75), (0.75, 0.75), (-0.75, 0.75)]

# Goal
GOAL_COLOR = formatColor(1, 0, 0)
GOAL_SCALE = 0.5

# Power position
POWER_SHAPE = [
    (-0.14, -1),
    (0.24, -0.404),
    (0.04, -0.333),
    (0.60, 0.088),
    (0.40, 0.193),
    (1, 1),
    (0, 0.404),
    (0.16, 0.298),
    (-0.52, -0.088),
    (-0.28, -0.263),
    (-1, -0.614)
]
POWER_COLOR = formatColor(1, 1, 0)
POWER_SCALE = 0.5

# Restart
RESTART_SHAPE = [
    (-1.000000, -0.520000),
    (-0.615385, -0.760000),
    (-0.576923, -1.000000),
    (0.384615, -1.000000),
    (0.423077, -0.760000),
    (1.000000, -0.520000),
    (0.692308, 0.120000),
    (1.000000, 1.000000),
    (0.230769, 0.800000),
    (0.346154, 0.560000),
    (-0.576923, 0.560000),
    (-0.384615, 0.800000),
    (-1.000000, 1.000000),
    (-0.769231, 0.120000)
]
RESTART_SCALE = 0.5
RESTART_COLOR = formatColor(1, 153 / 255, 0)


class InfoPane:
    scoreText = None

    def __init__(self, layout, gridSize):
        self.gridSize = gridSize
        self.width = layout.width * gridSize
        self.base = (layout.height + 1) * gridSize
        self.height = INFO_PANE_HEIGHT
        self.fontSize = 18
        self.drawPane()

    def toScreen(self, pos, y=None):
        """
          Translates a point relative from the bottom left of the info pane.
        """
        if y is None:
            x, y = pos
        else:
            x = pos

        x = self.gridSize + x  # Margin
        y = self.base + y
        return x, y

    def drawPane(self):
        self.scoreText = text(self.toScreen(0, 0), SCORE_COLOR, "SCORE:    0", "Times", self.fontSize, "bold")

    def updateScore(self, score):
        changeText(self.scoreText, "SCORE: % 4d" % score)


class GameGraphics:
    layout = None
    width = None
    height = None
    infoPane = None

    currentState = None
    agentImage = None

    def __init__(self, zoom=1.0, frameTime=0.0):
        self.agentImage = None
        self.zoom = zoom
        self.gridSize = DEFAULT_GRID_SIZE * zoom
        self.frameTime = frameTime

    def checkNullDisplay(self):
        return False

    def initialize(self, state):
        self.startGraphics(state)

        # self.drawDistributions(state)
        self.distributionImages = None  # Initialized lazily
        self.drawStaticObjects(state)
        self.drawAgentObjects(state)

        # Information
        self.previousState = state

    def startGraphics(self, state):
        self.layout = state.layout
        layout = self.layout
        self.width = layout.width
        self.height = layout.height
        self.make_window(self.width, self.height)
        self.infoPane = InfoPane(layout, self.gridSize)
        self.currentState = layout

    def drawStaticObjects(self, state):
        layout = self.layout
        self.drawWalls(layout.walls)
        self.drawGoToPowerPosition(layout.goToPowerPositions)
        self.drawPowerPosition(layout.powerPosition)
        self.drawRestart(layout.restartPositions)
        self.drawGoalPosition(layout.selectedGoalPosition)
        refresh()

    def drawAgentObjects(self, state):
        agent = state.agentState
        self.agentImage = (agent, self.drawAgent(agent))
        refresh()

    def update(self, newState):
        agentState = newState.agentState

        prevState, prevImage = self.agentImage
        self.agentImage = (agentState, prevImage)

        if agentState.jump:
            tempState = agentState.copy()
            tempState.configuration = agentState.jump
            self.animateAgent(tempState, prevState, prevImage)
            # prevState = tempState
        else:
            self.animateAgent(agentState, prevState, prevImage)

        self.infoPane.updateScore(newState.score)

    def make_window(self, width, height):
        grid_width = (width - 1) * self.gridSize
        grid_height = (height - 1) * self.gridSize
        screen_width = 2 * self.gridSize + grid_width
        screen_height = 2 * self.gridSize + grid_height + INFO_PANE_HEIGHT

        begin_graphics(screen_width,
                       screen_height,
                       BACKGROUND_COLOR,
                       "Reinforcement Learning")

    def drawAgent(self, agent):
        position = self.getPosition(agent)
        screen_point = self.to_screen(position)
        endpoints = self.getEndpoints(self.getDirection(agent))

        width = AGENT_OUTLINE_WIDTH
        outlineColor = AGENT_COLOR
        fillColor = AGENT_COLOR

        return [circle(screen_point, AGENT_SCALE * self.gridSize,
                       fillColor=fillColor, outlineColor=outlineColor,
                       endpoints=endpoints,
                       width=width)]

    def getEndpoints(self, direction, position=(0, 0)):
        x, y = position
        pos = x - int(x) + y - int(y)
        width = 30 + 80 * math.sin(math.pi * pos)

        delta = width / 2
        if direction == Directions.LEFT:
            endpoints = (180 + delta, 180 - delta)
        elif direction == Directions.UP:
            endpoints = (90 + delta, 90 - delta)
        elif direction == Directions.DOWN:
            endpoints = (270 + delta, 270 - delta)
        else:
            endpoints = (0 + delta, 0 - delta)
        return endpoints

    def moveAgent(self, position, direction, image_):
        screenPosition = self.to_screen(position)
        endpoints = self.getEndpoints(direction, position)
        r = AGENT_SCALE * self.gridSize
        moveCircle(image_[0], screenPosition, r, endpoints)
        refresh()

    def animateAgent(self, agent, prevAgent, image_):
        if self.frameTime < 0:
            print('Press any key to step forward, "q" to play')
            keys = wait_for_keys()
            if 'q' in keys:
                self.frameTime = 0.1
        if self.frameTime > 0.01 or self.frameTime < 0:
            start = time.time()
            fx, fy = self.getPosition(prevAgent)
            px, py = self.getPosition(agent)
            frames = 4.0
            for i in range(1, int(frames) + 1):
                pos = px * i / frames + fx * (frames - i) / frames, py * i / frames + fy * (frames - i) / frames
                self.moveAgent(pos, self.getDirection(agent), image_)
                refresh()
                sleep(abs(self.frameTime) / frames)
        else:
            self.moveAgent(self.getPosition(agent), self.getDirection(agent), image_)
        refresh()

    def getPosition(self, agentState):
        if agentState.configuration is None:
            return -1000, -1000
        return agentState.getPosition()

    def getDirection(self, agentState):
        if agentState.configuration is None:
            return Directions.UP
        return agentState.configuration.getDirection()

    def finish(self):
        end_graphics()

    def to_screen(self, point):
        (x, y) = point
        # y = self.height - y
        x = (x + 1) * self.gridSize
        y = (self.height - y) * self.gridSize
        return x, y

    # Fixes some TK issue with off-center circles
    def to_screen2(self, point):
        (x, y) = point
        # y = self.height - y
        x = (x + 1) * self.gridSize
        y = (self.height - y) * self.gridSize
        return x, y

    def drawWalls(self, wallMatrix):
        wallColor = WALL_COLOR
        for xNum, x in enumerate(wallMatrix):
            for yNum, cell in enumerate(x):
                if cell:  # There's a wall here
                    pos = (xNum, yNum)
                    screen = self.to_screen(pos)
                    screen2 = self.to_screen2(pos)

                    # draw each quadrant of the square based on adjacent walls
                    wIsWall = self.isWall(xNum - 1, yNum, wallMatrix)
                    eIsWall = self.isWall(xNum + 1, yNum, wallMatrix)
                    nIsWall = self.isWall(xNum, yNum + 1, wallMatrix)
                    sIsWall = self.isWall(xNum, yNum - 1, wallMatrix)
                    nwIsWall = self.isWall(xNum - 1, yNum + 1, wallMatrix)
                    swIsWall = self.isWall(xNum - 1, yNum - 1, wallMatrix)
                    neIsWall = self.isWall(xNum + 1, yNum + 1, wallMatrix)
                    seIsWall = self.isWall(xNum + 1, yNum - 1, wallMatrix)

                    # NE quadrant
                    if (not nIsWall) and (not eIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (0, 91), 'arc')
                    if nIsWall and (not eIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize * WALL_RADIUS, 0)),
                             add(screen, (self.gridSize * WALL_RADIUS, self.gridSize * (-0.5) - 1)), wallColor)
                    if (not nIsWall) and eIsWall:
                        # horizontal line
                        line(add(screen, (0, self.gridSize * (-1) * WALL_RADIUS)),
                             add(screen, (self.gridSize * 0.5 + 1, self.gridSize * (-1) * WALL_RADIUS)), wallColor)
                    if nIsWall and eIsWall and (not neIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize * 2 * WALL_RADIUS, self.gridSize * (-2) * WALL_RADIUS)),
                               WALL_RADIUS * self.gridSize - 1, wallColor, wallColor, (180, 271), 'arc')
                        line(add(screen, (self.gridSize * 2 * WALL_RADIUS - 1, self.gridSize * (-1) * WALL_RADIUS)),
                             add(screen, (self.gridSize * 0.5 + 1, self.gridSize * (-1) * WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize * WALL_RADIUS, self.gridSize * (-2) * WALL_RADIUS + 1)),
                             add(screen, (self.gridSize * WALL_RADIUS, self.gridSize * (-0.5))), wallColor)

                    # NW quadrant
                    if (not nIsWall) and (not wIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (90, 181), 'arc')
                    if nIsWall and (not wIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize * (-1) * WALL_RADIUS, 0)),
                             add(screen, (self.gridSize * (-1) * WALL_RADIUS, self.gridSize * (-0.5) - 1)), wallColor)
                    if (not nIsWall) and wIsWall:
                        # horizontal line
                        line(add(screen, (0, self.gridSize * (-1) * WALL_RADIUS)),
                             add(screen, (self.gridSize * (-0.5) - 1, self.gridSize * (-1) * WALL_RADIUS)), wallColor)
                    if nIsWall and wIsWall and (not nwIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize * (-2) * WALL_RADIUS, self.gridSize * (-2) * WALL_RADIUS)),
                               WALL_RADIUS * self.gridSize - 1, wallColor, wallColor, (270, 361), 'arc')
                        line(add(screen, (self.gridSize * (-2) * WALL_RADIUS + 1, self.gridSize * (-1) * WALL_RADIUS)),
                             add(screen, (self.gridSize * (-0.5), self.gridSize * (-1) * WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize * (-1) * WALL_RADIUS, self.gridSize * (-2) * WALL_RADIUS + 1)),
                             add(screen, (self.gridSize * (-1) * WALL_RADIUS, self.gridSize * (-0.5))), wallColor)

                    # SE quadrant
                    if (not sIsWall) and (not eIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (270, 361), 'arc')
                    if sIsWall and (not eIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize * WALL_RADIUS, 0)),
                             add(screen, (self.gridSize * WALL_RADIUS, self.gridSize * 0.5 + 1)), wallColor)
                    if (not sIsWall) and eIsWall:
                        # horizontal line
                        line(add(screen, (0, self.gridSize * 1 * WALL_RADIUS)),
                             add(screen, (self.gridSize * 0.5 + 1, self.gridSize * 1 * WALL_RADIUS)), wallColor)
                    if sIsWall and eIsWall and (not seIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize * 2 * WALL_RADIUS, self.gridSize * (2) * WALL_RADIUS)),
                               WALL_RADIUS * self.gridSize - 1, wallColor, wallColor, (90, 181), 'arc')
                        line(add(screen, (self.gridSize * 2 * WALL_RADIUS - 1, self.gridSize * (1) * WALL_RADIUS)),
                             add(screen, (self.gridSize * 0.5, self.gridSize * (1) * WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize * WALL_RADIUS, self.gridSize * (2) * WALL_RADIUS - 1)),
                             add(screen, (self.gridSize * WALL_RADIUS, self.gridSize * (0.5))), wallColor)

                    # SW quadrant
                    if (not sIsWall) and (not wIsWall):
                        # inner circle
                        circle(screen2, WALL_RADIUS * self.gridSize, wallColor, wallColor, (180, 271), 'arc')
                    if sIsWall and (not wIsWall):
                        # vertical line
                        line(add(screen, (self.gridSize * (-1) * WALL_RADIUS, 0)),
                             add(screen, (self.gridSize * (-1) * WALL_RADIUS, self.gridSize * 0.5 + 1)), wallColor)
                    if (not sIsWall) and wIsWall:
                        # horizontal line
                        line(add(screen, (0, self.gridSize * 1 * WALL_RADIUS)),
                             add(screen, (self.gridSize * (-0.5) - 1, self.gridSize * 1 * WALL_RADIUS)), wallColor)
                    if sIsWall and wIsWall and (not swIsWall):
                        # outer circle
                        circle(add(screen2, (self.gridSize * (-2) * WALL_RADIUS, self.gridSize * 2 * WALL_RADIUS)),
                               WALL_RADIUS * self.gridSize - 1, wallColor, wallColor, (0, 91), 'arc')
                        line(add(screen, (self.gridSize * (-2) * WALL_RADIUS + 1, self.gridSize * 1 * WALL_RADIUS)),
                             add(screen, (self.gridSize * (-0.5), self.gridSize * 1 * WALL_RADIUS)), wallColor)
                        line(add(screen, (self.gridSize * (-1) * WALL_RADIUS, self.gridSize * 2 * WALL_RADIUS - 1)),
                             add(screen, (self.gridSize * (-1) * WALL_RADIUS, self.gridSize * 0.5)), wallColor)

    def isWall(self, x, y, walls):
        if x < 0 or y < 0:
            return False
        if x >= walls.width or y >= walls.height:
            return False
        return walls[x][y]

    def drawGoToPowerPosition(self, objects):
        constant = self.gridSize * GO_TO_POWER_SCALE
        for pos in objects:
            screen_x, screen_y = self.to_screen(pos)
            coords = []
            for x, y in GO_TO_POWER_SHAPE:
                coords.append((x * constant + screen_x, y * constant + screen_y))

            polygon(coords, GO_TO_POWER_COLOR, filled=1)

    def drawGoalPosition(self, position):
        constant = self.gridSize * GOAL_SCALE
        screen_pos = self.to_screen(position)
        circle(screen_pos, constant, GOAL_COLOR, fillColor=GOAL_COLOR, width=1)

        t_x, t_y = screen_pos
        t_x -= constant // 2
        t_y -= constant // 1.5
        text((t_x, t_y), formatColor(0, 0, 0.5), "G", size=int(constant))

    def drawPowerPosition(self, position):
        constant = self.gridSize * POWER_SCALE
        s_x, s_y = self.to_screen(position)
        coords = []
        for x, y in POWER_SHAPE:
            coords.append((x * constant + s_x, y * constant + s_y))
        polygon(coords, formatColor(0, 0, 0), POWER_COLOR, filled=1, smoothed=0)

    def drawRestart(self, objects):
        constant = self.gridSize * RESTART_SCALE
        for pos in objects:
            screen_x, screen_y = self.to_screen(pos)
            coords = []
            for x, y in RESTART_SHAPE:
                coords.append((x * constant + screen_x, y * constant + screen_y))
            polygon(coords, formatColor(0, 0, 0), RESTART_COLOR, filled=1, smoothed=0)
            line(coords[2], coords[10], formatColor(0, 0, 0), 1)
            line(coords[3], coords[9], formatColor(0, 0, 0), 1)


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


# Saving graphical output
# -----------------------
# Note: to make an animated gif from this postscript output, try the command:
# convert -delay 7 -loop 1 -compress lzw -layers optimize frame* out.gif
# convert is part of imagemagick (freeware)

SAVE_POSTSCRIPT = False
POSTSCRIPT_OUTPUT_DIR = 'frames'
FRAME_NUMBER = 0


def saveFrame():
    """
    Saves the current graphical output as a postscript file
    """
    global SAVE_POSTSCRIPT, FRAME_NUMBER, POSTSCRIPT_OUTPUT_DIR
    if not SAVE_POSTSCRIPT:
        return
    if not os.path.exists(POSTSCRIPT_OUTPUT_DIR):
        os.mkdir(POSTSCRIPT_OUTPUT_DIR)
    name = os.path.join(POSTSCRIPT_OUTPUT_DIR, 'frame_%08d.ps' % FRAME_NUMBER)
    FRAME_NUMBER += 1
    writePostscript(name)  # writes the current canvas
