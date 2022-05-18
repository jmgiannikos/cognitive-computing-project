# import numpy as np

from operator import attrgetter
import datetime
from heapq import heappush, heappop
#Use deque instead of queue for performance reasons
from collections import deque
from . import log

PASSABLES = {"a": True, "g": True, "#": False, "t": True}

## Possible actions
NORTH = (-1,0)
SOUTH = (1,0)
WEST = (0,-1)
EAST = (0,1)
TURN_RIGHT = [[0,-1],[1,0]] # expressed as rotational matrix used for rotating a vector 90 degrees counterclockwise
TURN_LEFT = [[0,1],[-1,0]] # expressed as rotational matrix used for rotating a vector 270 degrees counterclockwise

ACTION_NAMES = {NORTH: "NORTH", SOUTH:"SOUTH", 
                WEST: "WEST", EAST: "EAST", TURN_RIGHT: "TURN RIGHT", TURN_LEFT: "TURN LEFT"}

COLOR_MAP = {"#": "gray", "g": "white", "": "black"}

TARGET_COLOR = "green"
TARGET_CHAR = "T"

class Tile(object):
    """
        Minimal class representing a grid/tile in the gridworld.
        Consists of a position in the 2d grid, a flag specifying if it is 
        passable or not as well as a set of neighbours.

        Only neighbour positions are contained, no reference to the actual
        neighbour tile object is stored to avoid multiple sources of truth!

        Parameters
        ----------
        element: char
            The string charactor used in the environment string to represent
            this tile.
        pos_x: int
            The position along the vertical-axis of this tile (counted from the
            top down).
        pos_y: int
            The position along the horizontal-axis of this tile (counted from 
            left to right).
        
        Attributes
        ----------
        char
        color
        pos: tuple
            A tuple combining pos_x and pos_y.
        passable: bool
            A boolean specifying if this tile is passable or not.
        neighbours: set
            A set containing the positions (and thus the keys for the tile dict 
            in the GridEnvironment) of the neighbouring tuples.
        target_visible: bool
            A flag used to mark this tile as being visible as a target.
            Is set by ``get_observation`` and used by the properties.
        is_target: bool
            Specifies whether this tile is a target or not in the current
            interaction.
        target_symbol: char
            The character this tile has as a target. Initially "".
        target_color: str
            A string representation for the color this target should have in
            the renderers.
        
    """

    def __init__(self, element, pos_x, pos_y):
        self.pos = (pos_x, pos_y)
        self._char = element
        self._original_element = element
        self.passable = None
        self._color = None
        self._parse_string(element)
        self.neighbours = set([]) 

        self.target_visible = False

        self.is_target = False
        self.target_symbol = ""
        self.target_color = None
        

    def _parse_string(self, element):
        self.passable = PASSABLES.get(element, True)
        self._color = COLOR_MAP.get(element, "black")

    @property
    def color(self):
        """
            Color property (str) of this tile. The color of a tile is dependent
            on whether or not this tile is a target and is actually visible as 
            a target.
        """
        if self.target_visible and self.is_target:
            return self.target_color
        return self._color

    @property
    def char(self):
        """
            The character property of this tile. In general the character of a 
            tile corresponds to its element when it was created, however targets
            may have different target characters.
        """
        if self.target_visible and self.is_target:
            return self.target_symbol
        return self._char

    def set_as_target(self, target_desc):
        """
            Updates this tile to be a potential target.

            Parameters
            ----------
            target_desc: dict
                A dictionary containing information about the target, such
                as its color and symbol.
        """

        self.is_target = True
        self.target_symbol = target_desc["symbol"]
        self.target_color = target_desc["color"]
        self._color = TARGET_COLOR
        self._char = TARGET_CHAR

    def unset_as_target(self):
        """
            Updates the tile to not be a potential target any longer.
        """
        self.is_target = False
        self.target_symbol = ""
        self.target_color = None
        self._color = COLOR_MAP.get(self._original_element, "black")
        self._char = self._original_element

    @classmethod
    def get_wall(cls):
        """
            Classmethod to return a dummy tile which is not passable. Is used
            as default value in the gridworld, when someone tries to access
            a tile position, which is out of bounds.
        """
        res= cls(None, -1, -1)
        res.passable = False
        return res

    @classmethod
    def invisible(cls):
        """
            Classmethod to return a generic "invisible" tile.
            The passable is None to represent "unknown", which requries special
            care when dealing with this elsewhere. 

            Returns
            ----------
                Tile
                A with attributes not set to any valid states since nothing is
                known regarding this tile.
        """
        res= cls("", None, None)
        res.passable = None
        return res

    def to_dict(self):
        """
            Gives a simplified dictionary (allows easy json conversion) of
            the tile.
                        
            Returns
            ------
                dict
                A dictionary containing the "passable", "color" and "symbol"
                keys. If targetVisible is set to true, the color will be
                the target color instead of the normal color.
        """
        return {"pos": list(self.pos), # Convert to list because of json
                "passable": self.passable, 
                "symbol": self.char,
                "color": self.color}

    def clone(self, passable=None):
        """
            Creates a complete copy of this tile. 

            Parameters
            ----------
            passable: bool, optional (Default: None)
                If given, the passable attribute will be overwritten to the
                one specified. Usually used to make "invisible" tiles 
                passable.

            Returns
            -------
                Tile
                A new tile object with attributes identical to this one.
        """
        res = Tile(self._original_element, self.pos[0], self.pos[1])
        # For the other attributes, we need to copy them manually as they
        # may have been changed manually
        res.passable = self.passable if passable is None else passable
        res._color = self._color
        res._char = self._char
        res.neighbours = set(self.neighbours)

        res.target_visible = self.target_visible
        res.is_target = self.is_target
        res.target_symbol = self.target_symbol
        res.target_color = self.target_color

        return res


class GridEnvironment(object):
    """
        Class representing 2 dimensional gridworlds while providing capabilities
        similar to OpenGym in that actions can be performed, once an agent has
        been specified. 

        Parameters
        ----------
        env_string: str, optional (Default: None)
            A string representing the environment. See ``parse_world_string`` 
            for more information.

        Attributes
        ----------
        tiles: dict
            A dictionary containing Tuple:Tile pairs. The tuple represents
            the position in the grid.
        size: tuple
            A tuple containing the size of the environment.
        agent_pos: tuple   
            A tuple containing the current position of the agent or None
            if no agent has been specified.
        initial_agent_pos: tuple
            The initial position of the agent when it was specified.
            Mainly used to create the log file correctly.
        view_radius: int, None
            The number of tiles the agent can see around itself. Initially
            None which means that the agent can see everything.
        target_radius: int, None
            The number of tiles in which the agent can distinguish a target.
            Ininitially None, which means that the agent can always distinguish
            the target.
        targets: list
            A list of tile positions which have been specified as targets.
        env_string: str
            The raw environment string specifying the layout of the grid as given
            to the init function.
        action_space: tuple
            A tuple containing all available actions of the gridworld. These
            are going ``NORTH``, ``SOUTH``, ``WEST``, ``EAST``, ``TURN_LEFT`` and ``TURN_RIGHT``,
            which move the agent in the respective direction by 1 block.
        _path: dict
            A private dictionary used to store optimal paths between nodes. Will
            be filled by ``compute_distance``, but is not explicitly invalidated
            in case the environment changes!
        log_path: str
            Path to the logfile. Initially None, which also means that the 
            environment should not do logging.
    """

    def __init__(self, env_string=None):
        self.tiles = {}
        self.size = (None, None)
        self.agent_pos = None
        self.initial_agent_pos = None
        self.view_radius = None
        self.target_radius = None
        self.targets = []
        self.facing_direction = NORTH # agent always starts facing north by default
        if env_string is not None:
            self.parse_world_string(env_string)
        self.action_space = (NORTH, SOUTH, WEST, EAST, TURN_LEFT, TURN_RIGHT)

        self._path = {} # Dictionary to store optimal paths between nodes
        self.log_path = None

        self.path_length = 0
        self.step_score = 0.0

    def set_logging(self, path, envName, agentType):
        """
            Defines that this environment should log all performed actions
            and other information, that might be required to replay actions.
            This will also trigger writing the currently stored details 
            regarding the environment into the logfile in a format readable
            by the playback agent.
            
            Parameters
            ----------
            path: str
                The path of the log-file. Can be absolute or relative to the 
                current working directory.
            envName: str
                The name of the environment that is currently used, given
                for logging purposes.
            agentType: str
                The name of the strategy of the agent that is currently used, given
                for logging purposes.
        """
        self.log_path = path
        visibles = [] if self.target_radius is not None else self.targets
        targets = {pos : {"color": self.tiles[pos].color, 
                        "symbol": self.tiles[pos].target_symbol} for pos in self.targets}
        goal = {"target": ("Unknown", "Unknown")}
        log(path, datetime.datetime.utcnow(), 
            "\nGridEnvironment Log:\n" \
            "EnvString: \n{}\n" \
            "AlwaysVisibles: {}\n" \
            "ViewRadius: {}\n" \
            "TargetRadius: {}\n" \
            "Targets: {}\n" \
            "Goal: {}\n" \
            "StartPosition: {}\n" \
            "Facing: {}\n" \
            "Name: {}\n" \
            "AgentType: {}\n".format(self.env_string,
                                        visibles, self.view_radius, 
                                        self.target_radius, targets, 
                                        goal, self.initial_agent_pos,
                                        self.facing_direction,
                                        envName, agentType))



    def initialize_agent(self, initial_agent_pos, view_radius=None):
        """
            Initializes the agent position, if it has not been done before.

            Parameters
            ----------
            initial_agent_pos: tuple
                The position the agent should start out with.
            view_radius: int, optional (Default: None)
                The radius in which the agent can see it's environment.
                Tiles outside this radius will be invisible.
        """
        if self.agent_pos is None:
            self.agent_pos = initial_agent_pos
            self.initial_agent_pos = initial_agent_pos
            self.view_radius = view_radius

    def initialize_targets(self, targets, target_radius=None):
        """
            Function to designate certain tiles as special targets, 
            which sets additional attributes of these tiles.
            
            Parameters
            ----------
            targets: dict
                A dictionary of dictionaries containing the target positions 
                as keys with another dictionary as value for each target
                containing color and symbol information about this target.
            target_radius: int, optional (Default: None)
                If given, specifies the radius in which targets are visible.
                None means, that targets are always visible.
        """

        # Reset old targets
        for t in self.targets:
            self.tiles[t].unset_as_target()

        for k,v in targets.items():
            self.tiles[k].set_as_target(v)

        self.targets = list(targets.keys())
        self.target_radius = target_radius

    def get_action_space(self):
        """
            Returns
            -------
                tuple
                A tuple of all available actions an agent can perform within 
                this environment. 
                All these actions are accepted by perform_action.
        """
        return self.action_space

    def perform_action(self, action):
        """
            Performs given action if possible.

            Parameter
            ---------
            action: Member of self.action_space
                The action which should be performed. If it is not a member
                of self.action_space, an exception will be raised.

            Returns
            -------
                tuple
                The new state of the agent after performing the action.
        """
        if not action in self.action_space:
            raise AttributeError("{} is not a valid action for this " \
                    "environment!".format(action))
        if self.agent_pos is None:
            raise AttributeError("No agent was initialized! Cannot perform " \
                            "action {}.".format(action))

        if self.log_path:
            log(self.log_path, datetime.datetime.utcnow(), "FUNCTION-{}".format(ACTION_NAMES[action]))

        if isinstance(action, list):
            if action == TURN_RIGHT:
                self._transform_facing_right()
                self.step_score += 0.6 ## at the moment turning is valued as two thirds as costly as stepping in a direction
            elif action == TURN_LEFT:
                self._transform_facing_left()
                self.step_score += 0.6
            else:
                raise AttributeError("{} is not a correct rotational matrix") ## should be caught ahead of this in all cases. More useful for testing code.
        else:
            x,y = self.agent_pos
            i,j = action
            if self.tiles[x+i,y+j].passable:
                self.agent_pos = (x+i, y+j)
                self.step_score += 1 ## TODO: check if we want to track all attempted or all successful steps. at the moment we are doing the latter.
                self.path_length += 1
        if self.agent_pos == self.targets[0] :
            log(self.log_path, datetime.datetime.utcnow(),  "Length: {}\n"\
                                                            "Action: {}\n".format(self.path_length,
                                                                                  self.step_score))
        return self.agent_pos

    def _rotate_vector_left(self, vec):
        x1 = vec[0]
        y1 = vec[1]

        # vector transformation: turn vector 270 degrees
        x2 = y1
        y2 = -x1

        return (x2,y2)

    def _rotate_vector_right(self, vec):
        x1 = vec[0]
        y1 = vec[1]

        # vector transformation: turn vector 270 degrees
        x2 = -y1
        y2 = x1

        return (x2, y2)

    def _transform_facing_left(self):
        x1 = self.facing_direction[0]
        y1 = self.facing_direction[1]

        self.facing_direction = self._rotate_vector_left((x1,y1))

    def _transform_facing_right(self):
        x1 = self.facing_direction[0]
        y1 = self.facing_direction[1]

        self.facing_direction = self._rotate_vector_right((x1,y1))

    def get_view_cone(self):
        if self.facing_direction == NORTH:
            viewcone = self._handle_octant(self.agent_pos, 5, self.view_radius) + self._handle_octant(self.agent_pos, 6, self.view_radius)
        elif self.facing_direction == SOUTH:
            viewcone = self._handle_octant(self.agent_pos, 1, self.view_radius) + self._handle_octant(self.agent_pos, 2, self.view_radius)
        elif self.facing_direction == EAST:
            viewcone = self._handle_octant(self.agent_pos, 0, self.view_radius) + self._handle_octant(self.agent_pos, 7, self.view_radius)
        elif self.facing_direction == WEST:
            viewcone = self._handle_octant(self.agent_pos, 3, self.view_radius) + self._handle_octant(self.agent_pos, 4, self.view_radius)
        else:
            raise EnvironmentError()

        viewcone = list(set(viewcone))

        return viewcone

    def parse_world_string(self, env_string, get_passable_states=False):
        r"""
            Parses an environment string, containing ``#`` for walls and ``g``
            for ground/free space. Rows are separated by ``\n``. Although it
            is not checked, but the provided world string should have a 
            rectangular shape.
            
            Parameters
            ---------
            env_string: string
                A string representation of the gridworld containing ``#``, ``g`` 
                and ``\n``.
            get_passable_states: boolean, optional (Default: False)
                If given, a list of all parsed passable states is returned, 
                which can be used as state-space for an MDP.
                
            Returns
            -------
                list
                A list of passable states if get_passable_states was specified,
                otherwise returns nothing.
        """
        self.env_string = env_string
        states = []
        for i, row in enumerate(env_string.split("\n")):#[::-1]):
            # print("row {}: {}".format(i, row))
            for j, element in enumerate(row):
                tile = Tile(element, i, j)
                self.tiles[tile.pos] = tile
                if tile.passable:
                    states.append(tile.pos)
        
        #Pretty bad hack, but should work since the string represents
        #the world from top left to bottom right
        maxPos = (i,j)
        #Add all neighbours
        for tile in self.tiles.values():
            for i,j in [(-1,0),(1,0),(0,-1),(0,1)]:
                newPos = (min(max(tile.pos[0]+i,0), maxPos[0]), 
                          min(max(tile.pos[1]+j,0),maxPos[1]))
                # if tile.passable and self.tiles[newPos].passable:
                # tile.neighbours.add(self.tiles[newPos])
                tile.neighbours.add(newPos)
        self.size = (maxPos[0]+1,maxPos[1]+1)
        if get_passable_states:
            return states

    def get_observation(self, json=False):
        """
            Creates a list of dictionaries representation (suitable for json)
            of the environment. Can "hide" parts of the environment with
            invisible tiles outside the Area of View around a given position.
            
            Parameters
            ----------
            json: bool (optional)
                If true, the Tiles will be converted to simple dictionaries
                before returning the result.
                
            Returns
            -------
                list of lists
                A 2 dimensional list, containing the visible tiles. 
                If json is set to true, it will return dict objects instead
                of Tile objects for easier serialization.
                Tiles outside of the Area of View will be replaced by generic
                "invisible" tiles.
        """
        res = []
        if self.view_radius is None:
            # Shortcut when we do not need to deal with lines of sight
            for i in range(self.size[0]):
                tmp = []
                for j in range(self.size[1]):
                    if (i,j) in self.targets:
                        if self.target_radius is None or self.is_visible((i,j), radius=self.target_radius):
                            self.tiles[(i,j)].target_visible = True
                        else:
                            self.tiles[(i,j)].target_visible = False

                    tmp.append(self.tiles[(i,j)].to_dict() if json \
                                                    else self.tiles[(i,j)])
                res.append(tmp)
        else:
            if self.agent_pos is None:
                raise ValueError("Requires agent_pos when view_radius is given!")

            agent_pos = tuple(self.agent_pos)

            # Compute Visibles
            visibles_map = []
            for octant in range(8):
                tmp = self._handle_octant(agent_pos, octant, 
                                                radius=self.view_radius)
                visibles_map += tmp
                                
            visibles_map = set(visibles_map)
            visibles_map.add(agent_pos)
            
            for i in range(self.size[0]):
                tmp = []
                for j in range(self.size[1]):
                    #TODO Consider making this more efficient,
                    # by not going over visibles every time!
                    if (i,j) not in visibles_map:
                        tmp.append(Tile.invisible().to_dict() if json \
                                                        else Tile.invisible())
                    else:
                        tmp.append(self.tiles[(i,j)].to_dict() if json \
                                                        else self.tiles[(i,j)])
                    if self.target_radius is None or self.is_visible((i,j), radius=self.target_radius):
                        self.tiles[(i,j)].target_visible = True
                    else:
                        self.tiles[(i,j)].target_visible = False
                res.append(tmp)
        return res
            

    def is_visible(self, position, radius=None):
        """
            Checks if the given position is currently visible from the 
            given current position.
            
            Parameters
            ----------
            position: tuple
                The position to check
            radius: int (Default: None)
                The radius in which tiles should be visible around a given
                position. If not given, the view radius is used.
                
            Returns
            -------
                bool
                True if the given position is visible from the current position
                given the radius, False otherwise.
        """
        
        if radius is None:
            radius = self.view_radius
        agent_pos = self.agent_pos
        x, y  = (position[0] - agent_pos[0]), (position[1] - agent_pos[1])
        
        # Determine the octant to check for visibility so that we do not need
        # to check the entire circle around us
        octant = [([1, 0], [2, 3]), ([6, 7], [5, 4])][x < 0][y < 0][abs(x) < abs(y)]
        visibles = self._handle_octant(agent_pos, octant, radius)
        
        return position in visibles

    def _handle_octant(self, agent_pos, octant, radius):
        r"""
            Computes the visible tiles within the given octant.
            
            Visibility algorithm adapted from:
            "https://blogs.msdn.microsoft.com/ericlippert/2011/12/12/
            shadowcasting-in-c-part-one/"
            
            However, I set up the octants as follows:
                                  
                               \ 5|6 / 
                              4 \ | / 7
                             ----------- 
                              3 / | \ 0
                               / 2|1 \
                               
            Parameters
            ---------
            agent_pos: tuple
                The agent position from which the octant is to be processed.
            octant: int
                The number of the currently processed octant.
            radius: int
                Visible radius.
                
            Returns
            -------
            visibles: list
                List of Tiles visible in the radius within the given
                octant.                
        """
        taskdeque = deque()
        # An item consists of: Column, Toprow, bottomrow
        visibles= []
        first_item = (1, 1, 0)
        taskdeque.append(first_item)
        while True:
            try:
                cur_item = taskdeque.popleft()
            except IndexError:
                break
            cur_column, top, bot = cur_item
            tmp = self._handle_column(agent_pos, cur_column, top, 
                                                    bot, taskdeque, octant, 
                                                    radius)
            visibles += tmp
        return visibles
    
    def _handle_column(self, agent_pos, col, top_slope, bot_slope, tasks, octant, 
                      radius):
        """
            Computes the visible tiles within the given column of the 
            given octant. Can distinguish between two different vision
            radii, e.g. to distinguish seeing walls and identifying more 
            details about blocks.
            
            Parameters
            ----------
            agentPos: tuple
                The position of the agent in the tile from which the visibility
                is to be computed.
            col: int
                The current column to be processed
            topSlope: float
                The current slope towards the highest still valid tile within
                the given column.
            botSlope: float
                The current slope towards the lowest still valid tile wihin
                the given column.
            tasks: list
                List of tasks (i.e. columns and slopes) still to process
            octant: int
                The currently processed octant.
            radius: int
                Visible radius.

                
            Returns
            -------
            visibilities: list
                List of Tiles visible in the radius within the given
                column.    
        """
        
        if col > radius:
            return []
        # Ignore inverted columns and columns that are too small
        if top_slope < bot_slope or abs(top_slope-bot_slope)*col < 0.001:
            return []
        
        col_lower = col-0.5
        
        bot_row = col_lower*bot_slope # Consider left edge for bot row
        if bot_row - int(bot_row) > 0.5:
            bot_row = int(bot_row+1)
        else:
            bot_row = int(bot_row)
        top_row = (col+0.5)*top_slope
        if top_row - int(top_row) > 0.5:
            top_row = int(top_row+1)
        else:
            top_row = int(top_row)
        world_shape = self.size
        # Make sure topRow is still within bounds
        top_row = min(top_row, world_shape[0]-1) 
        visibles = []
        last_row_transparent = None
        only_edges = False
        
        
        col_square = col_lower*col_lower
        
        for row in range(bot_row, top_row+1):
            row_lower = row-0.5
            row_lower_square = row_lower*row_lower
            # Break if we are outside the radius
            if radius != None and row_lower_square+col_square > radius*radius:
                break
            
            pos = self._transform_octant(octant, agent_pos, row, col)
            # Break if we are outside the world dimensions, ask for forgiveness
            try:   
                current_transparent = self.tiles[pos].passable
            except KeyError:
                #We must be outside our target area
                break
            # Add current tile to the visible positions
            # In order to show technically invisible edges, check for the
            # onlyEdges variable. If this is set, we only add non-transparent
            if row_lower_square+col_square <= radius*radius:
                if not only_edges or not current_transparent:
                    visibles.append(pos)
            # if not only_edges or not current_transparent:
            #     visibles.append(pos)
            
            # Check if we need to update slopes
            if not current_transparent:
                if last_row_transparent:
                    # Create new section
                    new_top_slope = row_lower/(col+0.5)
                    new_item = (col+1, new_top_slope, bot_slope)
                    tasks.append(new_item)
                    
                bot_slope = (row+0.5)/col_lower
                if not bot_slope < top_slope:
                    only_edges = True
                    
            last_row_transparent = current_transparent
            
        if last_row_transparent != None and last_row_transparent:
            new_item = (col+1, top_slope, bot_slope)
            tasks.append(new_item)
            
        return visibles
            
    def _transform_octant(self, octant, agent_pos, row, col):
        """
            Warpes the agentPosition so that it corresponds to the axis of the
            given octant.
            
            Parameters
            ---------
            octant: int
                The number of the given octant, see "handle_octant" for their
                placement.
            agent_pos: tuple
                The position to be transformed.
            row: int
                The currently considered row in the octant
            col: int
                The currently considered column in the octant
                
            Returns
            -------
                tuple
                The transformed agent position.
        """
        ax, ay = int(agent_pos[0]), int(agent_pos[1])

        #Quite costly as it takes around 0.1 second on 1 trail    
        if octant == 0:
            return (ax+row, ay+col)
        elif octant == 1:
            return (ax+col, ay+row)
        elif octant == 2:
            return (ax+col, ay-row)
        elif octant == 3:
            return (ax+row, ay-col)
        elif octant == 4:
            return (ax-row, ay-col)
        elif octant == 5:
            return (ax-col, ay-row)
        elif octant == 6:
            return (ax-col, ay+row)
        else:
            return (ax-row, ay+col)

    def compute_distance(self, start, goal, tiles=None):
        """
            Computes the distance between start and end using the A* algorithm.
            
            Parameters
            ----------
            start: tuple
                Start position for the A*
            goal: tuple
                Goal position
            tiles: dict, optional (Default: None)
                A dictionary containing tiles to be used. If not provided,
                the normal tiles in the environment will be used.
                
            Returns
            -------
                int or None
                The distance from the start to the end position if a way can
                be found, otherwise None
        """

        if tiles is None:
            tiles = dict(self.tiles)

        if not tiles[start].passable or not tiles[goal].passable:
            # Shortcut if either the start or goal tile are not passable
            return None

        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        frontier = []
        heappush(frontier, (0, start))

        while len(frontier) != 0:
            current = heappop(frontier)[1]
            
            if current == goal:
                break

            passable_neighbours = [n_pos for n_pos in tiles[current].neighbours 
                                                    if tiles[n_pos].passable]
            for n_pos in passable_neighbours: 
                new_cost = cost_so_far[current] + 1
                if n_pos not in cost_so_far or new_cost < cost_so_far[n_pos]:
                    cost_so_far[n_pos] = new_cost
                    priority = new_cost + self._heuristic(goal, n_pos)
                    # frontier.put(next, priority)
                    heappush(frontier, (priority, n_pos))
                    came_from[n_pos] = current

        # Store the optimal path for this start, goal pair
        self._path[(start,goal)] = dict(came_from)

        return cost_so_far.get(goal, None)

    def compute_distance_partially_visible(self, start, goal, visibles):
        """
            Computes the distance between start and end using the A* algorithm
            under the free space assumptiom, i.e. all unseen tiles are passable.

            This will not change the environment itself, meaning that which tiles
            have been seen, needs to be taken care of elsewhere.
            
            Parameters
            ----------
            start: tuple
                Start position for the A*
            goal: tuple
                Goal position
            visibles: iterable
                An iterable (set or list) containing all the tile positions,
                which should be considered known. All tiles, not in this
                iterable will be considered invisible and passable.
                
            Returns
            -------
                int or None
                The distance from the start to the end position if a way can
                be found, otherwise None
        """

        # Create shallow copy of tiles
        tmp_tiles = dict(self.tiles)

        # Set all "invisible" tiles to passable
        # We create new clone tiles for this
        for tile in tmp_tiles:
            if not tile in visibles:
                tmp_tiles[tile] = tmp_tiles[tile].clone(passable=True)

        # Compute distance using the altered tiles.
        dist = self.compute_distance(start, goal, tmp_tiles)

        return dist

    def _heuristic(self, a, b):
        """
            Heuristic for the A* algorithm, estimating the distance between
            to positions as the Manhattan distance.
            
            Parameters
            ----------
            start: tuple
                Start position
            end: tuple
                End position
                
            Returns
            -------
                float
                Estimated distance between the two given positions.
        """
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

if __name__ == "__main__":
    
    env_str = "######################\n" + \
                "#gggggggggggggggggggg#\n" + \
                "#g#g###g#g#g#g###g####\n" + \
                "#g#ggg#ggg#g#ggg#gggg#\n" + \
                "#g###g#####g###g#g##g#\n" + \
                "#g#ggg#ggg#g#gggggggg#\n" + \
                "#g#g###g###g#g###g####\n" + \
                "#ggggggg#ggg#gg##gggg#\n" + \
                "#g#######g#g#g##gg##g#\n" + \
                "#ggggggg###g###gg###g#\n" + \
                "#g#####gg##g##gg##g#g#\n" + \
                "#ggggg##gg#g#gg##gggg#\n" + \
                "#g###g###g#g#g#####gg#\n" + \
                "#ggggggggggggggg#gggg#\n" + \
                "######################"
    env = GridEnvironment(env_str)
    import time

    t0 = time.time()
    dist= env.compute_distance((1,1), (6,9))
    print("compute_distance took: {}s with res {}".format(time.time()-t0, 
                                                                dist))

