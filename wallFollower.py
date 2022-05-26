import logging
from cogmodel.gridEnvironment import TURN_RIGHT, TURN_LEFT
import numpy as np

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

        while(self.env.agent_pos != self.env.target):
            self._choose_action()

        # log footer of logging file
        if self.log:
            self.env.finish_experiment()

    def _choose_action(self):
        acted = False
        i = 0
        self.env.perform_action(TURN_LEFT, self)
        while i < 3 and not acted:
            for tile in self.env.get_view_cone:
                if tile.pos == (self.env.agent_pos[0]+self.env.facing_direction[0], self.env.agent_pos[0]+self.env.facing_direction[0]) and tile.passable:
                    self.env.perform_action(self.env.facing_direction, self)
                    acted = True
                    break
            self.env.perform_action(TURN_RIGHT, self)
            i += 1

