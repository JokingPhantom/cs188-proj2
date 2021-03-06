# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
      A reflex agent chooses an action at each choice point by examining
      its alternatives via a state evaluation function.

      The code below is provided as a guide.  You are welcome to change
      it in any way you see fit, so long as you don't touch our method
      headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {North, South, West, East, Stop}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        if successorGameState.isWin():
            return float("inf")

        valuePosition = successorGameState.getScore()

        # Only need to avoid ghosts to a certain extent
        ghostDistances = []
        for ghostState in newGhostStates:
            distance = manhattanDistance(ghostState.getPosition(), newPos)
            ghostDistances.append(distance)
            valuePosition += 3 * min(distance, 3)

        foodList = newFood.asList()
        foodList.sort(key=lambda pos: manhattanDistance(pos, newPos))
        valuePosition -= 1 * manhattanDistance(foodList[0], newPos)
        valuePosition += 9 * (currentGameState.getNumFood() - successorGameState.getNumFood())
        capsuleLocations = currentGameState.getCapsules()
        if successorGameState.getPacmanPosition() in capsuleLocations:
            valuePosition += 20
        if action == Directions.STOP:
            valuePosition -= 3
        return valuePosition

def scoreEvaluationFunction(currentGameState):
    """
      This default evaluation function just returns the score of the state.
      The score is the same one displayed in the Pacman GUI.

      This evaluation function is meant for use with adversarial search agents
      (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
      This class provides some common elements to all of your
      multi-agent searchers.  Any methods defined here will be available
      to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

      You *do not* need to make any changes here, but you can if you want to
      add functionality to all your adversarial search agents.  Please do not
      remove anything, however.

      Note: this is an abstract class: one that should not be instantiated.  It's
      only partially specified, and designed to be extended.  Agent (game.py)
      is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
      Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action from the current gameState using self.depth
          and self.evaluationFunction.

          Here are some method calls that might be useful when implementing minimax.

          gameState.getLegalActions(agentIndex):
            Returns a list of legal actions for an agent
            agentIndex=0 means Pacman, ghosts are >= 1

          gameState.generateSuccessor(agentIndex, action):
            Returns the successor game state after an agent takes an action

          gameState.getNumAgents():
            Returns the total number of agents in the game

          gameState.isWin():
            Returns whether or not the game state is a winning state

          gameState.isLose():
            Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        def maxValue(gameState, depth):
            legalActions = gameState.getLegalActions(0)
            if depth == self.depth or len(legalActions) == 0:
                return (self.evaluationFunction(gameState), None)
            actionScoreDict = {}
            for action in legalActions:
                newState = gameState.generateSuccessor(0, action)
                newScore = minValue(newState, 1, depth)[0]
                actionScoreDict[action] = newScore
            bestAction = max(actionScoreDict, key = actionScoreDict.get)
            return (actionScoreDict[bestAction], bestAction)

        def minValue(gameState, agentID, depth):
            legalActions = gameState.getLegalActions(agentID)
            if len(legalActions) == 0:
                return (self.evaluationFunction(gameState), None)
            actionScoreDict = {}
            for action in legalActions:
                newState = gameState.generateSuccessor(agentID, action)
                if (agentID == gameState.getNumAgents() - 1):
                    newScore = maxValue(newState, depth + 1)[0]
                else:
                    newScore = minValue(newState, agentID + 1, depth)[0]
                actionScoreDict[action] = newScore
            bestAction = min(actionScoreDict, key = actionScoreDict.get)
            return (actionScoreDict[bestAction], bestAction)

        return maxValue(gameState, 0)[1]

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
      Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        def maxValue(gameState, alpha, beta, depth):
            legalActions = gameState.getLegalActions(0)
            if depth == self.depth or len(legalActions) == 0:
                return (self.evaluationFunction(gameState), None)
            actionScoreDict = {}
            for action in legalActions:
                newState = gameState.generateSuccessor(0, action)
                newScore = minValue(newState, alpha, beta, 1, depth)[0]
                actionScoreDict[action] = newScore
                if newScore > beta:
                    return (newScore, action)
                alpha = max(alpha, newScore)
            bestAction = max(actionScoreDict, key = actionScoreDict.get)
            return (actionScoreDict[bestAction], bestAction)

        def minValue(gameState, alpha, beta, agentID, depth):
            legalActions = gameState.getLegalActions(agentID)
            if len(legalActions) == 0:
                return (self.evaluationFunction(gameState), None)
            actionScoreDict = {}
            for action in legalActions:
                newState = gameState.generateSuccessor(agentID, action)
                if (agentID == gameState.getNumAgents() - 1):
                    newScore = maxValue(newState, alpha, beta, depth + 1)[0]
                else:
                    newScore = minValue(newState, alpha, beta, agentID + 1, depth)[0]
                actionScoreDict[action] = newScore
                if newScore < alpha:
                    return (newScore, action)
                beta = min(beta, newScore)
            bestAction = min(actionScoreDict, key = actionScoreDict.get)
            return (actionScoreDict[bestAction], bestAction)

        return maxValue(gameState, float('-Inf'), float('Inf'), 0)[1]

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
          Returns the expectimax action using self.depth and self.evaluationFunction

          All ghosts should be modeled as choosing uniformly at random from their
          legal moves.
        """
        "*** YOUR CODE HERE ***"
        def maxValue(gameState, depth):
            legalActions = gameState.getLegalActions(0)
            if depth == self.depth or len(legalActions) == 0:
                return (self.evaluationFunction(gameState), None)
            actionScoreDict = {}
            for action in legalActions:
                newState = gameState.generateSuccessor(0, action)
                newScore = expValue(newState, 1, depth)[0]
                actionScoreDict[action] = newScore
            bestAction = max(actionScoreDict, key = actionScoreDict.get)
            return (actionScoreDict[bestAction], bestAction)

        def expValue(gameState, agentID, depth):
            legalActions = gameState.getLegalActions(agentID)
            if len(legalActions) == 0:
                return (self.evaluationFunction(gameState), None)
            actionScoreDict = {}
            newScore = 0
            for action in legalActions:
                newState = gameState.generateSuccessor(agentID, action)
                if (agentID == gameState.getNumAgents() - 1):
                    newScore += maxValue(newState, depth + 1)[0]
                else:
                    newScore += expValue(newState, agentID + 1, depth)[0]
                actionScoreDict[action] = newScore
            newScore = newScore / len(legalActions)
            return (newScore, None)

        return maxValue(gameState, 0)[1]


def betterEvaluationFunction(currentGameState):
    """
      Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
      evaluation function (question 5).

      DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    if currentGameState.isWin():
        return float("inf")
    if currentGameState.isLose():
        return - float("inf")
    valuePosition = currentGameState.getScore()
    curPos = currentGameState.getPacmanPosition()
    curFood = currentGameState.getFood().asList()
    curFood.sort(key=lambda pos: manhattanDistance(pos, curPos))
    closestFood = manhattanDistance(curFood[0], curPos)

    ghostStates = currentGameState.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
    numGhosts = len(ghostStates)

    # Only need to avoid ghosts to a certain extent
    ghostDistances = []
    for ghostState in ghostStates:
        distance = manhattanDistance(ghostState.getPosition(), curPos)
        ghostDistances.append(distance)
    closestGhost = min(ghostDistances)

    valuePosition += min(closestGhost, 4) * 2
    valuePosition -= closestFood * 1.5
    capsulelocations = currentGameState.getCapsules()
    valuePosition -= 4 * len(curFood)
    valuePosition -= 3.5 * len(capsulelocations)
    return valuePosition

# Abbreviation
better = betterEvaluationFunction
