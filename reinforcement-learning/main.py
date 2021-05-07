import os
import random
import sys

import layout
from core import ClassicGameRules
from game import Directions


def default(string):
    return string + ' [Default: %default]'


def parseAgentArgs(string):
    if string is None:
        return {}
    pieces = string.split(',')
    opts = {}
    for p in pieces:
        if '=' in p:
            key, val = p.split('=')
        else:
            key, val = p, 1
        opts[key] = val
    return opts


def readCommand(argv):
    """
    Processes the command used to run from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python main.py <options>
    EXAMPLES:   (1) python main.py --layout classic --zoom 2
                OR  python main.py -l classic -z 2
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default('the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='classic')
    parser.add_option('-a', '--agent', dest='agent',
                      help=default('the agent TYPE in the Agents module to use'),
                      metavar='TYPE', default='RAQ')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('--replay', dest='gameToReplay',
                      help='A recorded game file (pickle) to replay', default=None)
    parser.add_option('-o', '--agentArgs', dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    parser.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)
    parser.add_option('-p', '--pathPrint', dest='pathPrint', action='store_true',
                      help="Print path cost and followed path", default=False)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed:
        random.seed('hiren-chalodiya')

    # Choose a layout
    args['layout'] = layout.getLayout(options.layout)
    if args['layout'] is None:
        raise Exception("The layout " + options.layout + " cannot be found")

    # Choose a agent
    agentType = loadAgent(options.agent)
    agentOpts = parseAgentArgs(options.agentArgs)
    if options.numTraining > 0:
        args['numTraining'] = options.numTraining
        if 'numTraining' not in agentOpts:
            agentOpts['numTraining'] = options.numTraining
    agent = agentType(**agentOpts)  # Instantiate agent with agentArgs
    args['agent'] = agent

    # Don't display training games
    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    # Choose a display format
    if options.quietGraphics:
        import textDisplay
        args['display'] = textDisplay.NullGraphics()
    elif options.textGraphics:
        import textDisplay
        textDisplay.SLEEP_TIME = options.frameTime
        args['display'] = textDisplay.GameGraphics()
    else:
        pass
        import graphicsDisplay
        args['display'] = graphicsDisplay.GameGraphics(options.zoom, frameTime=options.frameTime)
    args['numGames'] = options.numGames
    args['record'] = options.record
    args['catchExceptions'] = options.catchExceptions
    args['timeout'] = options.timeout
    args['pathPrint'] = options.pathPrint

    # Special case: recorded games don't use the runGames method or args structure
    if options.gameToReplay is not None:
        print('Replaying recorded game %s.' % options.gameToReplay)
        import pickle
        f = open(options.gameToReplay, 'rb')
        try:
            recorded = pickle.load(f)
        finally:
            f.close()
        recorded['display'] = args['display']
        replayGame(**recorded)
        sys.exit(0)

    return args


def loadAgent(agent):
    # Looks through all pythonPath Directories for the right module,
    pythonPathDirs = ["."]

    for moduleDir in pythonPathDirs:
        if not os.path.isdir(moduleDir):
            continue
        moduleNames = [f for f in os.listdir(moduleDir) if f.endswith('gents.py')]
        for modulename in moduleNames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if agent in dir(module):
                return getattr(module, agent)
    raise Exception('The agent ' + agent + ' is not specified in any *Agents.py.')


def replayGame(layout, actions, display):
    import recordAgent
    rules = ClassicGameRules()
    agents = [recordAgent.RecordAgent(actions)]
    game = rules.newGame(layout, agents[0], display)
    state = game.state
    display.initialize(state.data)

    for action in actions:
        # Execute the action
        state = state.generateSuccessor(action)
        # Change the display
        display.update(state.data)
        # Allow for game specific conditions (winning, losing, etc.)
        rules.process(state, game)

    display.finish()


def runGames(layout, agent, display, numGames, record, pathPrint, numTraining=0, catchExceptions=False, timeout=30):
    import __main__
    __main__.__dict__['_display'] = display

    rules = ClassicGameRules(timeout)
    games = []

    printKnowledge = pathPrint

    for i in range(numGames):
        beQuiet = i < numTraining
        if beQuiet:
            # Suppress output and graphics
            import textDisplay
            gameDisplay = textDisplay.NullGraphics()
            rules.quiet = True
        else:
            gameDisplay = display
            rules.quiet = False
        game = rules.newGame(layout, agent, gameDisplay, beQuiet, catchExceptions)
        game.run()

        if printKnowledge and i == numTraining - 1:
            if 'stateActionPair' in dir(agent):
                positionDict: dict = dict()  # [UP, DOWN LEFT, RIGHT]
                for key, value in game.agent.stateActionPair.items():
                    state, action = key
                    value = f"{value:.2f}"
                    pos = state.data.agentState.configuration.pos
                    if pos not in positionDict:
                        positionDict[pos] = [None, None, None, None]
                    if action == Directions.UP:
                        positionDict[pos][0] = value
                    if action == Directions.DOWN:
                        positionDict[pos][1] = value
                    if action == Directions.LEFT:
                        positionDict[pos][2] = value
                    if action == Directions.RIGHT:
                        positionDict[pos][3] = value

                print("Knowledge base: (Position: UP, DOWN, LEFT, RIGHT)")
                for key, value in positionDict.items():
                    print(f"\t{key}: {value}")
                printKnowledge = False

        if not beQuiet:
            games.append(game)
            if pathPrint:
                print("\tPath followed: ", " ".join(game.moveHistory))

        if record and not beQuiet:
            import time
            import pickle
            fname = ('recorded-game-%d' % (i + 1)) + '-'.join([str(t) for t in time.localtime()[1:6]])
            f = open(fname, 'wb')
            components = {'layout': layout, 'actions': game.moveHistory}
            pickle.dump(components, f)
            f.close()

    if (numGames - numTraining) > 0:
        scores = [game.state.getScore() for game in games]
        print('Average Score:', sum(scores) / float(len(scores)))
        print('Scores:       ', ', '.join([str(score) for score in scores]))

    return games


if __name__ == '__main__':
    args = readCommand(sys.argv[1:])  # Get game components based on input
    runGames(**args)
