from game import Game, Actions, GameStateData


class AgentRules:
    """
    These functions govern how agent interacts with his environment under the classic game rules.
    """
    AGENT_SPEED = 1

    def getLegalActions(state):
        """
        Returns a list of possible actions.
        """
        return Actions.getPossibleActions(state.getAgentState().configuration, state.data.layout.walls)

    getLegalActions = staticmethod(getLegalActions)

    def applyAction(state, action):
        """
        Edits the state to reflect the results of the action.
        """
        legal = AgentRules.getLegalActions(state)
        if action not in legal:
            raise Exception("Illegal action " + str(action))

        agentState = state.data.agentState

        # Update Configuration
        vector = Actions.directionToVector(action, AgentRules.AGENT_SPEED)
        agentState.configuration = agentState.configuration.generateSuccessor(vector)

        # If Win then give 500 score and make _win to True
        if state.getAgentPosition() == state.data.layout.selectedGoalPosition:
            state.data._win = True
            state.data.scoreChange += 500

        # Update configuration in two special case
        layout = state.data.layout
        # case 1: Restart
        if layout.isRestart(agentState.getPosition()):
            agentState.jump = agentState.configuration
            agentState.configuration = agentState.configuration.jumpSuccessor(layout.getStart())
            state.data.scoreChange -= 50

        # case 2: power position
        if layout.isGoToPower(agentState.getPosition()):
            agentState.jump = agentState.configuration
            agentState.configuration = agentState.configuration.jumpSuccessor(layout.getPowerPosition())
            state.data.scoreChange += 100

    applyAction = staticmethod(applyAction)


class ClassicGameRules:
    """
    These game rules manage the control flow of a game, deciding when
    and how the game starts and ends.
    """
    initialState = None
    quiet = None

    def __init__(self, timeout=30):
        self.timeout = timeout

    def newGame(self, layout, agent, display, quiet=False, catchExceptions=False):
        initState = GameState()
        initState.initialize(layout)
        game = Game(agent, display, self, catchExceptions=catchExceptions)
        game.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return game

    def process(self, state, game):
        """
        Checks to see whether it is time to end the game.
        """
        if state.isWin():
            self.win(state, game)

    def win(self, state, game):
        if not self.quiet:
            print("Agent Reached !! Score: %d" % state.data.score)
        game.gameOver = True

    def agentCrash(self):
        print("Agent crashed")

    def getMaxTotalTime(self):
        return self.timeout

    def getMaxStartupTime(self):
        return self.timeout

    def getMoveWarningTime(self):
        return self.timeout

    def getMoveTimeout(self):
        return self.timeout

    def getMaxTimeWarnings(self):
        return 0


class GameState:
    """
    A GameState specifies the full game state,
    agent configurations and score changes.

    GameStates are used by the Game object to capture the actual state of the game and
    can be used by agents to reason about the game.

    Much of the information in a GameState is stored in a GameStateData object.  We
    strongly suggest that you access that data via the accessor methods below rather
    than referring to the GameStateData object directly.

    Note that in classic Pacman, Pacman is always agent 0.
    """

    ####################################################
    # Accessor methods: use these to access state data #
    ####################################################

    # static variable keeps track of which states have had getLegalActions called
    explored = set()

    def getAndResetExplored():
        tmp = GameState.explored.copy()
        GameState.explored = set()
        return tmp

    getAndResetExplored = staticmethod(getAndResetExplored)

    def getLegalActions(self):
        """
        Returns the legal actions for the agent specified.
        """
        if self.isWin():
            return []

        return AgentRules.getLegalActions(self)

    def generateSuccessor(self, action):
        """
        Returns the successor state after the specified agent takes the action.
        """
        # Check that successors exist
        if self.isWin():
            raise Exception('Can\'t generate a successor of a terminal state.')

        # Copy current state
        state = GameState(self)

        # Let agent's logic deal with its action's effects on the board
        AgentRules.applyAction(state, action)

        # Time passes
        state.data.scoreChange += -1

        # Book keeping
        state.data.score += state.data.scoreChange
        GameState.explored.add(self)
        GameState.explored.add(state)
        return state

    def getLegalAgentActions(self):
        return self.getLegalActions()

    def generateAgentSuccessor(self, action):
        """
        Generates the successor state after the specified pacman move
        """
        return self.generateSuccessor(action)

    def getAgentState(self):
        """
        Returns an AgentState object for pacman (in game.py)

        state.pos gives the current position
        state.direction gives the travel vector
        """
        return self.data.agentState.copy()

    def getAgentPosition(self):
        return self.data.agentState.getPosition()

    def getScore(self):
        return float(self.data.score)

    def getRestartPosition(self):
        return self.data.layout.restartPositions

    def getGoToPowerPosition(self):
        return self.data.layout.goToPowerPositions

    def getWalls(self):
        """
        Returns a Grid of boolean wall indicator variables.

        Grids can be accessed via list notation, so to check
        if there is a wall at (x,y), just call

        walls = state.getWalls()
        if walls[x][y] == True: ...
        """
        return self.data.layout.walls

    def hasWall(self, x, y):
        return self.data.layout.walls[x][y]

    def isWin(self):
        return self.data._win

    #############################################
    #             Helper methods:               #
    # You shouldn't need to call these directly #
    #############################################

    def __init__(self, prevState=None):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState is not None:  # Initial state
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy(self):
        state = GameState(self)
        state.data = self.data.deepCopy()
        return state

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        return hasattr(other, 'data') and self.data == other.data

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        return hash(self.data)

    def __str__(self):
        return str(self.data)

    def initialize(self, layout):
        """
        Creates an initial game state from a layout array (see layout.py).
        """
        self.data.initialize(layout)
