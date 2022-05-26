import logging
from cogmodel.gridEnvironment import TURN_RIGHT, TURN_LEFT
import numpy as np

MARK = None
FACING = (2, 2)


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

        # set up action queue with first step; assumption: face in direction we can walk in
        self._action_queue.append(self.env.facing_direction)

        # --- MAIN ROUTINE ---
        while(self.env.agent_pos != self.env.target):
            print( sorted(self._marked, key=lambda tup: tup[0]))
            # check how many actions are in queue and do all but one
            while(len(self._action_queue) > 1):
                # dequeue action to perform
                self._do_action()

            if not self._action_queue[0]:
                self._check_in_front()

            # check neighbors of current position
            self._check_neighbors()

            # --- CHOOSE ACTION ---
            # Case: not at intersection
            left = self._neighbors[0][1]
            front = self._neighbors[1][1]
            right = self._neighbors[2][1]
            if left and front and right:
                self._turn_around()
            elif left and right:
                self._action_queue.append(self.env.facing_direction)
            elif left and front:
                self._go_right(mark=False)
            elif right and front:
                self._go_left(mark=False)
            # Case: intersection
            else:
                tiles = np.array(self._neighbors, dtype=object)[:, 0]
                if not left and not front and not right:
                    # self._handle_intersection_one()
                    self._handle_intersection(
                        tiles, [self._go_left, self._go_front, self._go_right])
                elif not left and not front:
                    # self._handle_intersection_two()
                    self._handle_intersection(
                        tiles[:-1], [self._go_left, self._go_front])
                elif not front and not right:
                    # self._handle_intersection_three()
                    self._handle_intersection(
                        tiles[1:], [self._go_front, self._go_right])
                elif not left and not right:
                    # self._handle_intersection_four()
                    self._handle_intersection([tiles[0], tiles[2]], [
                                              self._go_left, self._go_right])


            print(self._action_queue)
            # do current action
            self._do_action()

        # log footer of logging file
        if self.log:
            self.env.finish_experiment()

    def _check_neighbors(self):
        """
            Checks neighbors of position agent will be in at the end of while-loop.
            In the following 0,1,2 are the checked neighbors, A is the current agent position and # is a tile:
            #1#
            0#2
            #A#
        """
        # ATTENTION: view cone has to have at least a radius of 2 otherwise we are doomed with this agent!
        observation = self.env.get_view_cone()
        facing = self.env.facing_direction
        x, y = self.env.agent_pos

        match facing:
            case (-1, 0):  # north
                self._neighbors[0] = [
                    (x-1, y-1), not ((x-1, y-1) in observation.keys() and observation.get((x-1, y-1)).passable)]
                self._neighbors[1] = [
                    (x-2, y), not ((x-2, y) in observation.keys() and observation.get((x-2, y)).passable)]
                self._neighbors[2] = [
                    (x-1, y+1), not ((x-1, y+1) in observation.keys() and observation.get((x-1, y+1)).passable)]
            case (0, 1):  # east
                self._neighbors[0] = [
                    (x-1, y+1), not ((x-1, y+1) in observation.keys() and observation.get((x-1, y+1)).passable)]
                self._neighbors[1] = [
                    (x, y+2), not ((x, y+2) in observation.keys() and observation.get((x, y+2)).passable)]
                self._neighbors[2] = [
                    (x+1, y+1), not ((x+1, y+1) in observation.keys() and observation.get((x+1, y+1)).passable)]
            case (1, 0):  # south
                self._neighbors[0] = [
                    (x+1, y+1), not ((x+1, y+1) in observation.keys() and observation.get((x+1, y+1)).passable)]
                self._neighbors[1] = [
                    (x+2, y), not ((x+2, y) in observation.keys() and observation.get((x+2, y)).passable)]
                self._neighbors[2] = [
                    (x+1, y-1), not ((x+1, y-1) in observation.keys() and observation.get((x+1, y-1)).passable)]
            case (0, -1):  # west
                self._neighbors[0] = [
                    (x+1, y-1), not ((x+1, y-1) in observation.keys() and observation.get((x+1, y-1)).passable)]
                self._neighbors[1] = [
                    (x, y-2), not ((x, y-2) in observation.keys() and observation.get((x, y-2)).passable)]
                self._neighbors[2] = [
                    (x-1, y-1), not ((x-1, y-1) in observation.keys() and observation.get((x-1, y-1)).passable)]

    def _do_action(self):
        """
            Performs action that is first in action queue.
        """
        action = self._action_queue.pop(0)
        if action == FACING:
            self.env.perform_action(
                action=self.env.facing_direction, agent=self)
        elif action:
            self.env.perform_action(action=action, agent=self)
        else:
            self._marked.append(self.env.agent_pos)

    def _check_in_front(self, checks=0):
        """
            Checks if tile in front is passable. If so adds step forward, else turns around.
        """
        facing = self.env.facing_direction
        x, y = self.env.agent_pos

        match facing:
            case (-1, 0):  # north
                tile_in_front = (x-1, y)
            case (0, 1):  # east
                tile_in_front = (x, y+1)
            case (1, 0):  # south
                tile_in_front = (x+1, y)
            case (0, -1):  # west
                tile_in_front = (x, y-1)

        if self.env.tiles[tile_in_front].passable:
            self._action_queue.append(facing)
        else:
            match checks:
                case 0:
                    self.env.perform_action(action=TURN_LEFT, agent=self)
                    self._check_in_front(checks=1)
                case 1:
                    self.env.perform_action(action=TURN_RIGHT, agent=self)
                    self.env.perform_action(action=TURN_RIGHT, agent=self)
                    self._check_in_front(checks=2)
                case 2:
                    self.env.perform_action(action=TURN_RIGHT, agent=self)
                    self._marked.append(self.env.agent_pos)
                    self._action_queue.append(facing)

    def _turn_around(self):
        """
            Adds action to queue that make agent turn around.
        """
        self._action_queue.append(TURN_LEFT)
        self._action_queue.append(TURN_LEFT)
        self._action_queue.append(FACING)

    def _go_right(self, mark=True):
        """
            Adds action to queue that make agent go right.
        """
        self._action_queue.append(TURN_RIGHT)
        self._action_queue.append(FACING)
        if mark:
            self._action_queue.append(MARK)

    def _go_front(self, mark=True):
        """
            Adds action to queue that make agent follow current direction.
        """
        self._action_queue.append(self.env.facing_direction)
        if mark:
            self._action_queue.append(MARK)

    def _go_left(self, mark=True):
        """
            Adds action to queue that make agent go left.
        """
        self._action_queue.append(TURN_LEFT)
        self._action_queue.append(FACING)
        if mark:
            self._action_queue.append(MARK)

    def _handle_intersection(self, free_neighbors, action_functions):
        """
        Handles intersections via tremaux algorithm rules.
        ---------------------------------------------------
        Args:
            free_neighbors [(x,y)]: List containing tuples with coordinates of free (non wall) neighbor tiles. Length is between 2 and 3.
            action_functions [function]: list of action functions (_turn_around, _go_left, _go_front, _go_right). Function i should be invoke if direction i in free_neighbors is chosen
        """

        # mark current position
        self._marked.append(self.env.agent_pos)

        # Intersection is unknown
        if sum(tile in self._marked for tile in free_neighbors) == 0:
            # selecting random direction
            dir = np.random.randint(0, len(free_neighbors))
            action_functions[dir]()

         # intersection is known
        else:
            if self._marked.count(self.env.agent_pos) == 1:  # found a loop
                # mark current position and turn around
                self._marked.append(self.env.agent_pos)
                self._turn_around()
            else:  # already searched whole area
                minimum_mark_value = np.min(
                    [self._marked.count(x) for x in free_neighbors])
                minimal_neighbors = [
                    x for x in free_neighbors if self._marked.count(x) == minimum_mark_value]
                chosen_one = minimal_neighbors[np.random.randint(
                    0, len(minimal_neighbors))]
                dir = list(free_neighbors).index(chosen_one)
                action_functions[dir]()

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
