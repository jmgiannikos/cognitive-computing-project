import math

from cogmodel.gridEnvironment import TURN_RIGHT, TURN_LEFT
import numpy as np

MAX_STEPS = 1000
AGENT_AMBITION = 1  # 1 should be the base value here. This means that any field which has been visited less and is an actual improvement distance wise is chosen immediately
BACKSTEP_PENALTY = 4


class greedy(object):
    """
        uses a greedy heuristic to navigate labyrinth
    """

    def __init__(self, gridEnvironment):
        self.env = gridEnvironment  # env on which agent runs
        self.visited = {gridEnvironment.agent_pos: 1}
        self.last_pos = gridEnvironment.agent_pos
        self.options = []

    def run(self):
        """
            Starts the algorithm on labyrinth given in self.env
        """

        # log header of logging file
        self.env.start_experiment()

        i = 0
        while(self.env.agent_pos != self.env.target and i < MAX_STEPS):
            self._choose_action()
            i += 1

        if i == MAX_STEPS:
            print("agent death termination")
        else:
            print("goal found")
        # log footer of logging file
        self.env.finish_experiment()

    def _choose_action(self):
        i = 0
        acted = False
        while i < 4 and not acted:
            for tile in self.env.get_view_cone():
                if tile == (self.env.agent_pos[0] + self.env.facing_direction[0],
                            self.env.agent_pos[1] + self.env.facing_direction[1]) and self.env.tiles[tile].passable:
                    if self.tile_score(tile) < self.tile_score(self.env.agent_pos)-AGENT_AMBITION:
                        self.last_pos = self.env.agent_pos
                        self.env.perform_action(
                            self.env.facing_direction, self)
                        acted = True
                        if self.env.agent_pos in self.visited.keys():
                            self.visited[self.env.agent_pos] += 1
                        else:
                            self.visited[self.env.agent_pos] = 1
                    else:
                        self.options.append((self.tile_score(tile), tile))
                    break
            if not acted:
                self.env.perform_action(TURN_RIGHT, self)
            i += 1
        if not acted:
            best_option = self.calc_best_option()
            self.last_pos = self.env.agent_pos
            self.env.perform_action(
                (best_option[0]-self.env.agent_pos[0], best_option[1]-self.env.agent_pos[1]), self)
            if self.env.agent_pos in self.visited.keys():
                self.visited[self.env.agent_pos] += 1
            else:
                self.visited[self.env.agent_pos] = 1
        self.options = []

    def tile_score(self, tile):
        visited_score = 0
        if tile in self.visited.keys():
            visited_score = self.visited[tile]
        if tile == self.last_pos:
            visited_score += BACKSTEP_PENALTY
        distance_score = math.sqrt((tile[0]-self.env.target[0])**2)/self.env.size[0] + \
            math.sqrt((tile[1]-self.env.target[1])**2)/self.env.size[1]
        return visited_score + distance_score

    def calc_best_option(self):
        best_option = None
        for option in self.options:
            if best_option is None or best_option[0] > option[0]:
                best_option = option
        return best_option[1]
