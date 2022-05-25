import logging
from cogmodel.gridEnvironment import NORTH, SOUTH, WEST, EAST, TURN_RIGHT, TURN_LEFT
import numpy as np

MARK = None


class tremaux(object):
    """
        Uses the trémaux method to solve labyrinths.
    """

    def __init__(self, gridEnvironment, logging):
        self.env = gridEnvironment  # env on which agent runs
        self.log = logging  # sets if logging is active
        self._action_queue = []  # enqueues/dequeues action to be performed by agent
        # neighbor-coordinates on left/front/right
        self._neighbors = [(), (), ()]
        self._marked = []  # marked tiles saved as tuples

    def run(self):
        """
            Starts the algorithm on labyrinth given in self.env
        """

        # log header of logging file
        if self.log:
            self.env.start_experiment()

        # --- MAIN ROUTINE ---
        while(self.env.agent_pos != self.env.target):
            print("Q")
            print(self._action_queue)

            # check how many actions are in queue and do all but one
            while(len(self._action_queue) > 1):
                # dequeue action to perform
                self._do_action()

            self._check_neighbors()

            # --- CHOOSE ACTION ---
            # Case: not at intersection
            left = not self.env.tiles[self._neighbors[0]].passable
            front = not self.env.tiles[self._neighbors[1]].passable
            right = not self.env.tiles[self._neighbors[2]].passable
            if left and right:
                self._action_queue.append(self.env.facing_direction)
            elif left and front and right:
                self._action_queue.append(TURN_LEFT)
                self._action_queue.append(TURN_LEFT)
                self._action_queue.append(self.env.facing_direction)
            elif left and front:
                self._action_queue.append(TURN_RIGHT)
                self._action_queue.append(self.env.facing_direction)
            elif right and front:
                self._action_queue.append(TURN_LEFT)
                self._action_queue.append(self.env.facing_direction)
            # Case: intersection
            else:
                if not left and not front and not right:
                    self._handle_intersection_one()
                elif not left and not front:
                    self._handle_intersection_two()
                elif not right and not front:
                    self._handle_intersection_three()
                elif not left and not right:
                    self._handle_intersection_four()

             # do current action
            self._do_action()

        # log footer of logging file
        if self.log:
            self.env.finish_experiment()

    def _check_neighbors(self):
        # ATTENTION: view cone has to have at least a radius of 2 otherwise we are doomed with this agent!
        facing = self.env.facing_direction
        x, y = self.env.agent_pos

        match facing:
            case (-1, 0):  # north
                self._neighbors[0] = (x-1, y-1)
                self._neighbors[1] = (x-2, y)
                self._neighbors[2] = (x-1, y+1)
            case (0, 1):  # east
                self._neighbors[0] = (x-1, y+1)
                self._neighbors[1] = (x, y+2)
                self._neighbors[2] = (x+1, y+1)
            case (1, 0):  # south
                self._neighbors[0] = (x+1, y+1)
                self._neighbors[1] = (x+2, y)
                self._neighbors[2] = (x+1, y-1)
            case (0, -1):  # west
                self._neighbors[0] = (x+1, y-1)
                self._neighbors[1] = (x, y-2)
                self._neighbors[2] = (x-1, y-1)

    def _do_action(self):
        action = self._action_queue.pop(0)
        if action:
            self.env.perform_action(action=action, agent=self)
        else:
            self._marked.append(self.env.agent_pos)

    def _turn_around(self):
        self._action_queue.append(TURN_LEFT)
        self._action_queue.append(TURN_LEFT)
        self._action_queue.append(self.env.facing_direction)

    def _go_right(self):
        self._action_queue.append(TURN_RIGHT)
        self._action_queue.append(self.env.facing_direction)
        self._action_queue.append(MARK)

    def _go_front(self):
        self._action_queue.append(self.env.facing_direction)
        self._action_queue.append(MARK)

    def _go_left(self):
        self._action_queue.append(TURN_LEFT)
        self._action_queue.append(self.env.facing_direction)
        self._action_queue.append(MARK)

    def _handle_intersection_one(self):
        """
            Intersection type : +
        """
        # mark current position
        self._marked.append(self.env.agent_pos)

        # Intersection is unknown
        if sum(tile in self._marked for tile in self._neighbors) == 0:
            dir = np.random.randint(1, 4)
            if dir == 1:  # go left
                self._go_left()
            elif dir == 2:  # go front
                self._go_front()
            else:  # go right
                self._go_right()

        # intersection is known
        else:
            if self._marked.count(self.env.agent_pos) == 1:  # found a loop
                # mark current position
                self._marked.append(self.env.agent_pos)
                # add actions to queue
                self._turn_around()
            else:  # already searched whole area
                minimum_mark_value = np.min(
                    [self._marked.count(x) for x in self._neighbors])
                minimal_neighbors = [
                    x for x in self._neighbors if self._marked.count(x) == minimum_mark_value]
                chosen_one = minimal_neighbors[np.random.randint(
                    0, len(minimal_neighbors))]
                if chosen_one == self._neighbors[0]:  # left is chosen
                    self._go_left()
                elif chosen_one == self._neighbors[1]:  # front is chosen
                    self._go_front()
                else:  # right is chosen
                    self._go_right()

    def _handle_intersection_two(self):
        """
            Intersection type : -|
        """
        # mark current position
        self._marked.append(self.env.agent_pos)

        # Intersection is unknown
        if sum(tile in self._marked for tile in self._neighbors) == 0:
            dir = np.random.randint(1, 3)
            if dir == 1:  # go left
                self._go_left()
            elif dir == 2:  # go front
                self._go_front()

        # intersection is known
        else:
            if self._marked.count(self.env.agent_pos) == 1:  # found a loop
                # mark current position
                self._marked.append(self.env.agent_pos)
                # add actions to queue
                self._turn_around()
            else:  # already searched whole area
                minimum_mark_value = np.min(
                    [self._marked.count(x) for x in self._neighbors])
                minimal_neighbors = [
                    x for x in self._neighbors if self._marked.count(x) == minimum_mark_value and self.env.tiles[x].passable]
                chosen_one = minimal_neighbors[np.random.randint(
                    0, len(minimal_neighbors))]
                if chosen_one == self._neighbors[0]:  # left is chosen
                    self._go_left()
                elif chosen_one == self._neighbors[1]:  # front is chosen
                    self._go_front()

    def _handle_intersection_three(self):
        """
            Intersection type : |-
        """
        # mark current position
        self._marked.append(self.env.agent_pos)

        # Intersection is unknown
        if sum(tile in self._marked for tile in self._neighbors) == 0:
            dir = np.random.randint(1, 3)
            if dir == 1:  # go front
                self._go_front()
            else:  # go right
                self._go_right()

        # intersection is known
        else:
            if self._marked.count(self.env.agent_pos) == 1:  # found a loop
                # mark current position
                self._marked.append(self.env.agent_pos)
                # add actions to queue
                self._turn_around()
            else:  # already searched whole area
                minimum_mark_value = np.min(
                    [self._marked.count(x) for x in self._neighbors])
                minimal_neighbors = [
                    x for x in self._neighbors if self._marked.count(x) == minimum_mark_value and self.env.tiles[x].passable]
                chosen_one = minimal_neighbors[np.random.randint(
                    0, len(minimal_neighbors))]
                if chosen_one == self._neighbors[2]:  # right is chosen
                    self._go_right()
                elif chosen_one == self._neighbors[1]:  # front is chosen
                    self._go_front()

    def _handle_intersection_four(self):
        """
            Intersection type : T
        """
        # mark current position
        self._marked.append(self.env.agent_pos)

        # Intersection is unknown
        if sum(tile in self._marked for tile in self._neighbors) == 0:
            dir = np.random.randint(1, 3)
            if dir == 1:  # go left
                self._go_left()
            else:  # go right
                self._go_right()

        # intersection is known
        else:
            if self._marked.count(self.env.agent_pos) == 1:  # found a loop
                # mark current position
                self._marked.append(self.env.agent_pos)
                # add actions to queue
                self._turn_around()
            else:  # already searched whole area
                minimum_mark_value = np.min(
                    [self._marked.count(x) for x in self._neighbors])
                minimal_neighbors = [
                    x for x in self._neighbors if self._marked.count(x) == minimum_mark_value and self.env.tiles[x].passable]
                chosen_one = minimal_neighbors[np.random.randint(
                    0, len(minimal_neighbors))]
                if chosen_one == self._neighbors[0]:  # left is chosen
                    self._go_left()
                elif chosen_one == self._neighbors[2]:  # right is chosen
                    self._go_right()
