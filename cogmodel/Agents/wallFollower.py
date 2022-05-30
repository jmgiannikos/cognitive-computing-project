import logging
from cogmodel.gridEnvironment import TURN_RIGHT, TURN_LEFT
import numpy as np

MAX_STEPS = 1000

class wallFollower(object):
    """
        Uses the left hand rule method to solve labyrinths.
    """

    def __init__(self, gridEnvironment, logging):
        self.env = gridEnvironment  # env on which agent runs
        self.log = logging  # sets if logging is active

    def run(self):
        """
            Starts the algorithm on labyrinth given in self.env
        """

        # log header of logging file
        if self.log:
            self.env.start_experiment()

        i = 0
        while(self.env.agent_pos != self.env.target and i<MAX_STEPS):
            self._choose_action()
            i += 1

        if i == MAX_STEPS:
            print("agent death termination")
        else:
            print("goal found")
        # log footer of logging file
        if self.log:
            self.env.finish_experiment()

    def _choose_action(self):
        acted = False
        i = 0
        self.env.perform_action(TURN_LEFT, self)
        while i < 3 and not acted:
            for tile in self.env.get_view_cone():
                if tile == (self.env.agent_pos[0]+self.env.facing_direction[0], self.env.agent_pos[1]+self.env.facing_direction[1]) and self.env.tiles[tile].passable:
                    self.env.perform_action(self.env.facing_direction, self)
                    acted = True
                    break
            if not acted:
                self.env.perform_action(TURN_RIGHT, self)
                i += 1


