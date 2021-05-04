from abc import ABC, abstractmethod


class Environment(ABC):

    @abstractmethod
    def getCurrentState(self):
        """
        Returns the current state of enviornment
        """

    @abstractmethod
    def getPossibleActions(self, state):
        """
          Returns possible actions the agent
          can take in the given state. Can
          return the empty list if we are in
          a terminal state.
        """

    @abstractmethod
    def doAction(self, action):
        """
          Performs the given action in the current
          environment state and updates the enviornment.

          Returns a (reward, nextState) pair
        """

    @abstractmethod
    def reset(self):
        """
          Resets the current state to the start state
        """

    def isTerminal(self):
        """
          Has the enviornment entered a terminal
          state? This means there are no successors
        """
        state = self.getCurrentState()
        actions = self.getPossibleActions(state)
        return len(actions) == 0
