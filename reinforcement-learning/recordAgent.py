from game import Agent


class RecordAgent(Agent):
    actions = None
    count = None

    def __init__(self, actions):
        super().__init__()
        self.actions = actions
        self.count = -1

    def getAction(self, state):
        self.count += 1
        return self.actions[self.count]
