from abc import ABC, abstractmethod


class MarkovDecisionProcess(ABC):

    @abstractmethod
    def getStates(self):
        """
        Return a list of all states in the MDP.
        Not generally possible for large MDPs.
        """

    @abstractmethod
    def getStartState(self):
        """
        Return the start state of the MDP.
        """

    @abstractmethod
    def getPossibleActions(self, state):
        """
        Return list of possible actions from 'state'.
        """

    @abstractmethod
    def getTransitionStatesAndProbs(self, state, action):
        """
        Returns list of (nextState, prob) pairs
        representing the states reachable
        from 'state' by taking 'action' along
        with their transition probabilities.

        Note that in Q-Learning and reinforcement
        learning in general, we do not know these
        probabilities nor do we directly model them.
        """

    @abstractmethod
    def getReward(self, state, action, nextState):
        """
        Get the reward for the state, action, nextState transition.

        Not available in reinforcement learning.
        """

    @abstractmethod
    def isTerminal(self, state):
        """
        Returns true if the current state is a terminal state.  By convention,
        a terminal state has zero future rewards.  Sometimes the terminal state(s)
        may have no possible actions.  It is also common to think of the terminal
        state as having a self-loop action 'pass' with zero reward; the formulations
        are equivalent.
        """
