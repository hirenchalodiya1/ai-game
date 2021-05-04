from util import *
import time
import traceback
import sys


#######################
# Parts worth reading #
#######################

class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # inspects the starting state
    """

    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
        must return an action from Directions.{UP, DOWN, RIGHT, LEFT}
        """
        raiseNotDefined()


class Directions:
    UP = 'Up'
    DOWN = 'Down'
    LEFT = 'Left'
    RIGHT = 'Right'


class Configuration:
    """
    A Configuration holds the (x,y) coordinate of a character, along with its
    traveling direction.

    The convention for positions, like a graph, is that (0,0) is the lower left corner, x increases
    horizontally and y increases vertically.  Therefore, up is the direction of increasing y, or (0,1).
    """

    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction

    def getPosition(self):
        return self.pos

    def getDirection(self):
        return self.direction

    def isInteger(self):
        x, y = self.pos
        return x == int(x) and y == int(y)

    def __eq__(self, other):
        if other is None:
            return False
        return self.pos == other.pos and self.direction == other.direction

    def __hash__(self):
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self):
        return "(x,y)=" + str(self.pos) + ", " + str(self.direction)

    def generateSuccessor(self, vector):
        """
        Generates a new configuration reached by translating the current
        configuration by the action vector.  This is a low-level call and does
        not attempt to respect the legality of the movement.

        Actions are movement vectors.
        """
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        return Configuration((x + dx, y + dy), direction)

    def jumpSuccessor(self, pos):
        return Configuration(pos, Directions.UP)


class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, scared, etc).
    """

    def __init__(self, startConfiguration):
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.jump = None

    def __str__(self):
        return "Agent: " + str(self.configuration)

    def __eq__(self, other):
        if other is None:
            return False
        return self.configuration == other.configuration

    def __hash__(self):
        return hash(self.configuration)

    def copy(self):
        state = AgentState(self.start)
        state.configuration = self.configuration
        return state

    def getPosition(self):
        if self.configuration is None:
            return None
        return self.configuration.getPosition()

    def getDirection(self):
        return self.configuration.getDirection()


class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists.  Data is accessed
    via grid[x][y] where (x,y) are positions on a map with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner.

    The __str__ method constructs an output that is oriented like a board.
    """

    def __init__(self, width, height, initialValue=False, bitRepresentation=None):
        if initialValue not in [False, True]:
            raise Exception('Grids can only contain booleans')
        self.CELLS_PER_INT = 30

        self.width = width
        self.height = height
        self.data = [[initialValue for _ in range(height)] for __ in range(width)]
        if bitRepresentation:
            self._unpackBits(bitRepresentation)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __str__(self):
        out = [[str(self.data[x][y])[0] for x in range(self.width)] for y in range(self.height)]
        out.reverse()
        return '\n'.join([''.join(x) for x in out])

    def __eq__(self, other):
        if other is None:
            return False
        return self.data == other.data

    def __hash__(self):
        # return hash(str(self))
        base = 1
        h = 0
        for L in self.data:
            for i in L:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self):
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self):
        return self.copy()

    def shallowCopy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item=True):
        return sum([x.count(item) for x in self.data])

    def asList(self, key=True):
        List = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key:
                    List.append((x, y))
        return List

    def packBits(self):
        """
        Returns an efficient int list representation

        (width, height, bitPackedInts...)
        """
        bits = [self.width, self.height]
        currentInt = 0
        for i in range(self.height * self.width):
            bit = self.CELLS_PER_INT - (i % self.CELLS_PER_INT) - 1
            x, y = self._cellIndexToPosition(i)
            if self[x][y]:
                currentInt += 2 ** bit
            if (i + 1) % self.CELLS_PER_INT == 0:
                bits.append(currentInt)
                currentInt = 0
        bits.append(currentInt)
        return tuple(bits)

    def _cellIndexToPosition(self, index):
        x = index / self.height
        y = index % self.height
        return x, y

    def _unpackBits(self, bits):
        """
        Fills in data from a bit-level representation
        """
        cell = 0
        for packed in bits:
            for bit in self._unpackInt(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height:
                    break
                x, y = self._cellIndexToPosition(cell)
                self[x][y] = bit
                cell += 1

    def _unpackInt(self, packed, size):
        bools = []
        if packed < 0:
            raise ValueError("must be a positive integer")
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                bools.append(True)
                packed -= n
            else:
                bools.append(False)
        return bools


def reconstituteGrid(bitRep):
    if isinstance(bitRep, tuple):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation=bitRep[2:])


####################################
# Parts you shouldn't have to read #
####################################

class Actions:
    """
    A collection of static methods for manipulating move actions.
    """
    # Directions
    _directions = {Directions.UP: (0, 1),
                   Directions.DOWN: (0, -1),
                   Directions.LEFT: (-1, 0),
                   Directions.RIGHT: (1, 0)}

    _directionsAsList = _directions.items()

    TOLERANCE = .001

    def reverseDirection(action):
        if action == Directions.UP:
            return Directions.DOWN
        if action == Directions.DOWN:
            return Directions.UP
        if action == Directions.LEFT:
            return Directions.RIGHT
        if action == Directions.RIGHT:
            return Directions.LEFT
        return action

    reverseDirection = staticmethod(reverseDirection)

    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.UP
        if dy < 0:
            return Directions.DOWN
        if dx < 0:
            return Directions.LEFT
        if dx > 0:
            return Directions.RIGHT
        raise Exception("Null vector")

    vectorToDirection = staticmethod(vectorToDirection)

    def directionToVector(direction, speed=1.0):
        dx, dy = Actions._directions[direction]
        return dx * speed, dy * speed

    directionToVector = staticmethod(directionToVector)

    def getPossibleActions(config, walls):
        possible = []
        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight
        if abs(x - x_int) + abs(y - y_int) > Actions.TOLERANCE:
            return [config.getDirection()]

        for direction, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]:
                possible.append(direction)
        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    def getLegalNeighbors(position, walls):
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for direction, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width:
                continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height:
                continue
            if not walls[next_x][next_y]:
                neighbors.append((next_x, next_y))
        return neighbors

    getLegalNeighbors = staticmethod(getLegalNeighbors)

    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return x + dx, y + dy

    getSuccessor = staticmethod(getSuccessor)


class GameStateData:
    agentState: AgentState = None

    def __init__(self, prevState=None):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        self.scoreChange = 0
        self._win = False
        if prevState is not None:
            self.agentState = prevState.agentState.copy()
            self.layout = prevState.layout
            self.score = prevState.score

            # if agent is in goal state then it's win
            self._win = self.agentState.configuration.pos == self.layout.selectedGoalPosition

    def deepCopy(self):
        state = GameStateData(self)
        state.layout = self.layout.deepCopy()
        return state

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        return other is not None and (self.agentState == other.agentState and self.score == other.score)

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        return int((hash(self.agentState) + 13 * hash(self.score)) % 1048575)

    def __str__(self):
        width, height = self.layout.width, self.layout.height
        map_ = Grid(width, height)
        walls = self.layout.walls
        # walls
        for x in range(width):
            for y in range(height):
                map_[x][y] = "%" if walls[x][y] else " "

        # agent
        if self.agentState is not None and self.agentState.configuration is not None:
            x, y = [int(i) for i in nearestPoint(self.agentState.configuration.pos)]
            map_[x][y] = "A"

        # goal
        x, y = self.layout.selectedGoalPosition
        map_[x][y] = "G"

        # go to power position
        for x, y in self.layout.goToPowerPositions:
            map_[x][y] = "o"

        # power position
        x, y = self.layout.powerPosition
        map_[x][y] = "O"

        # restart
        for x, y in self.layout.restartPositions:
            map_[x][y] = "R"

        return str(map_) + ("\nScore: %d\n" % self.score)

    def initialize(self, layout):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.layout = layout
        self.score = 0
        self.scoreChange = 0

        self.agentState = AgentState(Configuration(layout.agentPosition, Directions.UP))

        # check win condition
        self._win = self.agentState.configuration.pos == self.layout.selectedGoalPosition


class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    """
    state = None  # handles current state
    numMoves = 0

    def __init__(self, agent, display, rules, startingIndex=0, muteAgents=False, catchExceptions=False):
        self.agentCrashed = False
        self.agent = agent
        self.display = display
        self.rules = rules
        self.startingIndex = startingIndex
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTime = 0
        self.totalAgentTimeWarning = 0
        self.agentTimeout = False
        from io import StringIO
        self.agentOutput = StringIO()

    def _agentCrash(self, quiet=False):
        """Helper method for handling agent crashes"""
        if not quiet:
            traceback.print_exc()
        self.gameOver = True
        self.agentCrashed = True
        self.rules.agentCrash()

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self):
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR
        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput
        sys.stderr = self.agentOutput

    def unmute(self):
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR

    def run(self):
        """
        Main control loop for game play.
        """
        self.display.initialize(self.state.data)
        self.numMoves = 0

        ##############################################
        # inform learning agents of the game start   #
        ##############################################
        agent = self.agent
        if not agent:
            self.mute()
            # this is a null agent, meaning it failed to load
            # the other team wins
            sys.stderr.write("Agent failed to load")
            self.unmute()
            self._agentCrash(quiet=True)
            return

        if "registerInitialState" in dir(agent):
            self.mute()
            if self.catchExceptions:
                try:
                    timed_func = TimeoutFunction(agent.registerInitialState, int(self.rules.getMaxStartupTime()))
                    try:
                        start_time = time.time()
                        timed_func(self.state.deepCopy())
                        time_taken = time.time() - start_time
                        self.totalAgentTime += time_taken
                    except TimeoutFunctionException:
                        sys.stderr.write("Agent ran out of time on startup!")
                        self.unmute()
                        self.agentTimeout = True
                        self._agentCrash(quiet=True)
                        return
                except Exception:
                    self._agentCrash(quiet=False)
                    self.unmute()
                    return
            else:
                agent.registerInitialState(self.state.deepCopy())
            self.unmute()

        ###################################
        # Main Loop                       #
        ###################################

        while not self.gameOver:
            # Fetch the next agent
            agent = self.agent
            move_time = 0
            skip_action = False
            observation = None

            # Generate an observation of the state
            if 'observationFunction' in dir(agent):
                self.mute()
                if self.catchExceptions:
                    try:
                        timed_func = TimeoutFunction(agent.observationFunction, int(self.rules.getMoveTimeout()))
                        start_time = time.time()
                        try:
                            observation = timed_func(self.state.deepCopy())
                        except TimeoutFunctionException:
                            skip_action = True
                        move_time += time.time() - start_time
                        self.unmute()
                    except Exception:
                        self._agentCrash(quiet=False)
                        self.unmute()
                        return
                else:
                    observation = agent.observationFunction(self.state.deepCopy())
                self.unmute()
            else:
                observation = self.state.deepCopy()

            # Solicit an action
            self.mute()
            if self.catchExceptions:
                try:
                    timed_func = TimeoutFunction(agent.getAction, int(self.rules.getMoveTimeout()) - int(move_time))
                    try:
                        start_time = time.time()
                        if skip_action:
                            raise TimeoutFunctionException()
                        action = timed_func(observation)
                    except TimeoutFunctionException:
                        sys.stderr.write("Agent timed out on a single move!")
                        self.agentTimeout = True
                        self._agentCrash(quiet=True)
                        self.unmute()
                        return
                    move_time += time.time() - start_time

                    if move_time > self.rules.getMoveWarningTime():
                        self.totalAgentTimeWarning += 1
                        sys.stderr.write("Agent took too long to make a move! This is warning %d" % self.totalAgentTimeWarning)
                        if self.totalAgentTimeWarning > self.rules.getMaxTimeWarning:
                            sys.stderr.write("Agent exceeded the maximum number of warnings: %d" % self.totalAgentTimeWarning)
                            self.agentTimeout = True
                            self._agentCrash(quiet=True)
                            self.unmute()
                            return

                    self.totalAgentTime += move_time
                    if self.totalAgentTime > self.rules.getMaxTotalTime:
                        sys.stderr.write("Agent ran out of time! (time: %1.2f)" % self.totalAgentTime)
                        self.agentTimeout = True
                        self._agentCrash(quiet=True)
                        self.unmute()
                        return
                    self.unmute()
                except Exception:
                    self._agentCrash()
                    self.unmute()
                    return
            else:
                action = agent.getAction(observation)
            self.unmute()

            # Execute the action
            self.moveHistory.append(action)
            if self.catchExceptions:
                try:
                    self.state = self.state.generateSuccessor(action)
                except Exception:
                    self.mute()
                    self._agentCrash()
                    self.unmute()
                    return
            else:
                self.state = self.state.generateSuccessor(action)

            # Change the display
            self.display.update(self.state.data)

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)

            # Track progress
            self.numMoves += 1

        #################################
        # Loop ended                    #
        #################################

        # inform a learning agent of the game result
        agent = self.agent
        if "final" in dir(agent):
            try:
                self.mute()
                agent.final(self.state)
                self.unmute()
            except Exception:
                if not self.catchExceptions:
                    raise
                self._agentCrash()
                self.unmute()
                return

        self.display.finish()
