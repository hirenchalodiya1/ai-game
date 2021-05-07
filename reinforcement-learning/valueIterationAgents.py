import util

from learningAgents import ValueEstimationAgent


# TODO: Make default MDP class inherited from mdp.py
class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """

    def __init__(self, mdp, discount=0.9, iterations=100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter()  # A Counter is a dict with default 0
        self.actions = {state: None for state in self.mdp.getStates()}
        # Write value iteration code here
        for _ in range(self.iterations):
            next_values = util.Counter()
            for state in self.mdp.getStates():
                max_value = float('-inf')
                for action in self.mdp.getPossibleActions(state):
                    v = self.computeQValueFromValues(state, action)
                    if v > max_value:
                        max_value = v
                        next_values[state] = v
                        self.actions[state] = action
            self.values = next_values

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]

    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        qvalue = 0
        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            qvalue += prob * (self.mdp.getReward(state, action, nextState) + self.discount * self.values[nextState])
        return qvalue

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        return self.actions[state]

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        """Returns the policy at the state (no exploration)."""
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)


# Abbreviation
vI = ValueIterationAgent
