import time

DRAW_EVERY = 1
SLEEP_TIME = 0  # This can be overwritten by __init__
DISPLAY_MOVES = False
QUIET = False  # Suppresses output


class NullGraphics:
    def initialize(self, state, isBlue=False):
        pass

    def update(self, state):
        pass

    def checkNullDisplay(self):
        return True

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        print(state)

    def updateDistributions(self, dist):
        pass

    def finish(self):
        pass


class GameGraphics:
    turn = 0

    def __init__(self, speed=None):
        if speed is not None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def initialize(self, state):
        self.draw(state)
        self.pause()
        self.turn = 0

    def update(self, state):
        self.turn += 1
        if DISPLAY_MOVES:
            pass

        if self.turn % DRAW_EVERY == 0:
            self.draw(state)
            self.pause()

        if state._win:
            self.draw(state)

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        print(state)

    def finish(self):
        pass
