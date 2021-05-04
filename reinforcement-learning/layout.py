from util import manhattanDistance
from game import Grid
import os
import random

VISIBILITY_MATRIX_CACHE = {}


class Layout:
    """
    A Layout manages the static information about the game board.
    """

    def __init__(self, layoutText, copy=False):
        self.width = len(layoutText[0])
        self.height = len(layoutText)
        self.layoutText = layoutText

        # Go to power position
        self.goToPowerPositions = []
        # Power position
        self.powerPosition = None

        # Goal
        self.goalPositions = []
        self.selectedGoalPosition = None

        # Restart position
        self.restartPositions = []

        # Walls
        self.walls = Grid(self.width, self.height, False)

        # Agent position
        self.agentPosition = None

        self.processLayoutText(layoutText)
        if not copy:
            self.choose_goal()

    def isWall(self, pos):
        x, col = pos
        return self.walls[x][col]

    def isRestart(self, pos):
        return pos in self.restartPositions

    def getStart(self):
        return self.agentPosition

    def isGoToPower(self, pos):
        return pos in self.goToPowerPositions

    def getPowerPosition(self):
        return self.powerPosition

    def getRandomLegalPosition(self):
        x = random.choice(range(self.width))
        y = random.choice(range(self.height))
        while self.isWall((x, y)):
            x = random.choice(range(self.width))
            y = random.choice(range(self.height))
        return x, y

    def getRandomCorner(self):
        poses = [(1, 1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        return random.choice(poses)

    def getFurthestCorner(self, position):
        poses = [(1, 1), (1, self.height - 2), (self.width - 2, 1), (self.width - 2, self.height - 2)]
        dist, pos = max([(manhattanDistance(p, position), p) for p in poses])
        return pos

    def __str__(self):
        return "\n".join(self.layoutText)

    def deepCopy(self):
        layout = Layout(self.layoutText[:], True)
        layout.selectedGoalPosition = self.selectedGoalPosition
        return layout

    def processLayoutText(self, layoutText):
        """
        Coordinates are flipped from the input format to the (x,y) convention here

        The shape of the maze.  Each character
        represents a different type of object.
         % - Wall
         G - Goal
         p - Go to power position
         P - Power position
         R - Restart
         S - Start Position
        Other characters are ignored.
        """
        maxY = self.height - 1
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = layoutText[maxY - y][x]
                self.processLayoutChar(x, y, layoutChar)

    def processLayoutChar(self, x, y, layoutChar):
        if layoutChar == '%':
            self.walls[x][y] = True
        elif layoutChar == 'G':
            self.goalPositions.append((x, y))
        elif layoutChar == 'p':
            self.goToPowerPositions.append((x, y))
        elif layoutChar == 'P':
            self.powerPosition = (x, y)
        elif layoutChar == "R":
            self.restartPositions.append((x, y))
        elif layoutChar == "S":
            self.agentPosition = (x, y)

    def choose_goal(self):
        import random
        self.selectedGoalPosition = random.choice(self.goalPositions)


def getLayout(name, back=2):
    if name.endswith('.lay'):
        layout = tryToLoad('layouts/' + name)
        if layout is None:
            layout = tryToLoad(name)
    else:
        layout = tryToLoad('layouts/' + name + '.lay')
        if layout is None:
            layout = tryToLoad(name + '.lay')
    if layout is None and back >= 0:
        curdir = os.path.abspath('.')
        os.chdir('..')
        layout = getLayout(name, back - 1)
        os.chdir(curdir)
    return layout


def tryToLoad(fullname):
    if not os.path.exists(fullname):
        return None
    f = open(fullname)
    try:
        return Layout([line.strip() for line in f])
    finally:
        f.close()
