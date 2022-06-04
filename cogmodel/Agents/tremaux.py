import logging
from cogmodel.gridEnvironment import TURN_RIGHT, TURN_LEFT
import numpy as np

MARK = None
FACING = (2, 2)
CHECK_FUTURE = (3, 3)


class tremaux(object):
    """
        Uses the trémaux method to solve labyrinths.
    """

    def __init__(self, gridEnvironment):
        self.env = gridEnvironment  # env on which agent runs
        self._action_queue = []  # enqueues/dequeues action to be performed by agent
        # neighbor-coordinates on left/front/right and bool if wall as tuple
        self._neighbors = [(), (), ()]
        self._marked = []  # marked tiles saved as triples

    def run(self):
        """
            Starts the algorithm on labyrinth given in self.env
        """

        # log header of logging file
        self.env.start_experiment()

        # set up action queue with first step; assumption: face in direction we can walk in
        self._first_action()

        # --- MAIN ROUTINE ---
        while (self.env.agent_pos != self.env.target):
            # check how many actions are in queue and do all but one
            while (len(self._action_queue) > 1):
                if self._action_queue[0] == CHECK_FUTURE:
                    self._action_queue.pop(0)
                    break
                # dequeue action to perform
                self._do_action()

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

            # do current action
            self._do_action()

        # log footer of logging file
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
                    (x - 1, y - 1, 1),
                    not ((x - 1, y - 1) in observation.keys() and observation.get((x - 1, y - 1)).passable)]
                self._neighbors[1] = [
                    (x - 2, y, 2), not ((x - 2, y) in observation.keys() and observation.get((x - 2, y)).passable)]
                self._neighbors[2] = [
                    (x - 1, y + 1, 3),
                    not ((x - 1, y + 1) in observation.keys() and observation.get((x - 1, y + 1)).passable)]
            case (0, 1):  # east
                self._neighbors[0] = [
                    (x - 1, y + 1, 2),
                    not ((x - 1, y + 1) in observation.keys() and observation.get((x - 1, y + 1)).passable)]
                self._neighbors[1] = [
                    (x, y + 2, 3), not ((x, y + 2) in observation.keys() and observation.get((x, y + 2)).passable)]
                self._neighbors[2] = [
                    (x + 1, y + 1, 0),
                    not ((x + 1, y + 1) in observation.keys() and observation.get((x + 1, y + 1)).passable)]
            case (1, 0):  # south
                self._neighbors[0] = [
                    (x + 1, y + 1, 3),
                    not ((x + 1, y + 1) in observation.keys() and observation.get((x + 1, y + 1)).passable)]
                self._neighbors[1] = [
                    (x + 2, y, 0), not ((x + 2, y) in observation.keys() and observation.get((x + 2, y)).passable)]
                self._neighbors[2] = [
                    (x + 1, y - 1, 1),
                    not ((x + 1, y - 1) in observation.keys() and observation.get((x + 1, y - 1)).passable)]
            case (0, -1):  # west
                self._neighbors[0] = [
                    (x + 1, y - 1, 0),
                    not ((x + 1, y - 1) in observation.keys() and observation.get((x + 1, y - 1)).passable)]
                self._neighbors[1] = [
                    (x, y - 2, 1), not ((x, y - 2) in observation.keys() and observation.get((x, y - 2)).passable)]
                self._neighbors[2] = [
                    (x - 1, y - 1, 2),
                    not ((x - 1, y - 1) in observation.keys() and observation.get((x - 1, y - 1)).passable)]

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
            self.mark_tile()

    def _first_action(self, checks=0):
        """
        handles starting conditions
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
                    self._first_action(checks=1)
                case 1:
                    self.env.perform_action(action=TURN_LEFT, agent=self)
                    self._first_action(checks=2)
                case 2:
                    self.env.perform_action(action=TURN_LEFT, agent=self)
                    self._first_action(checks=3)
                case 3:
                    raise AttributeError("You fucked up!")

    def _turn_around(self):
        """
            Adds action to queue that make agent turn around.
        """
        self._action_queue.append(TURN_LEFT)
        self._action_queue.append(TURN_LEFT)
        self._action_queue.append(CHECK_FUTURE)
        self._action_queue.append(FACING)

    def _go_right(self, mark=True):
        """
            Adds action to queue that make agent go right.
        """
        self._action_queue.append(TURN_RIGHT)
        self._action_queue.append(CHECK_FUTURE)
        self._action_queue.append(FACING)
        if mark:
            self._action_queue.append(MARK)

    def _go_front(self, mark=True):
        """
            Adds action to queue that make agent follow current direction.
        """
        if mark:
            self._action_queue.append(CHECK_FUTURE)
        self._action_queue.append(self.env.facing_direction)
        if mark:
            self._action_queue.append(MARK)

    def _go_left(self, mark=True):
        """
            Adds action to queue that make agent go left.
        """
        self._action_queue.append(TURN_LEFT)
        self._action_queue.append(CHECK_FUTURE)
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
        self.mark_tile(goin_in=True)

        # Intersection is unknown
        if sum(tile in self._marked for tile in free_neighbors) == 0:
            # selecting random direction

            dir = np.random.randint(0, len(free_neighbors))
            action_functions[dir]()

        # intersection is known
        else:
            x, y = self.env.agent_pos
            match self.env.facing_direction:
                case (-1, 0):
                    tmp = (x, y, 0)
                case (0, 1):
                    tmp = (x, y, 1)
                case (1, 0):
                    tmp = (x, y, 2)
                case (0, -1):
                    tmp = (x, y, 3)
            if self._marked.count(tmp) == 1:  # found a loop
                # mark current position and turn around
                self.mark_tile(goin_in=True)
                self._action_queue.pop(0)
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

    def mark_tile(self, goin_in=False):
        x, y = self.env.agent_pos
        match self.env.facing_direction:
            case (-1, 0):
                if goin_in:
                    tmp = (x, y, 0)
                else:
                    tmp = (x, y, 2)
            case (0, 1):
                if goin_in:
                    tmp = (x, y, 1)
                else:
                    tmp = (x, y, 3)
            case (1, 0):
                if goin_in:
                    tmp = (x, y, 2)
                else:
                    tmp = (x, y, 0)
            case (0, -1):
                if goin_in:
                    tmp = (x, y, 3)
                else:
                    tmp = (x, y, 1)
        self._marked.append(tmp)
