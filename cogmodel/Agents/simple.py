from cmath import sqrt
import logging

from soupsieve import match
from cogmodel.gridEnvironment import SOUTH, EAST, WEST, TURN_RIGHT, TURN_LEFT, NORTH, ACTION_MAPPING
import numpy as np


class simple(object):

    def __init__(self, gridEnvironment):
        self.env = gridEnvironment  # env on which agent runs
        # neighbor-coordinates on left/front/right and bool if wall as tuple
        self._possible_actions = []

        self.rotation_matrix = np.array([[1, 0], [0, 1]])

        if self.env.facing_direction == EAST:
            # If facing east, we need to rotate the vectors by 270 degrees counterclockwise to make the agents "North" face actual east
            self.rotation_matrix = np.array([[0, 1], [-1, 0]])

        if self.env.facing_direction == SOUTH:
            # If facing east, we need to rotate the vectors by 180 degrees counterclockwise to make the tiles the agents "North" face actual east (or
            # mirror the vector)
            self.rotation_matrix = np.array([[-1, 0], [0, -1]])

        if self.env.facing_direction == WEST:
            # If facing West, we need to rotate the vectors by 90 degrees counterclockwise to make the agents "North" face actual east
            self.rotation_matrix = np.array([[0, -1], [1, 0]])

    def run(self):
        # log header of logging file
        self.env.start_experiment()

        #print("Facing Start")
        # print(self.env.facing_direction)

        self.get_surroundings()

        #print("Facing After 1st")
        # print(self.env.facing_direction)
        while(self.env.agent_pos != self.env.target):
            #dist = sqrt((self.env.agent_pos[0]-self.env.target[0])**2+(self.env.agent_pos[1]-self.env.target[1])**2)
            # print(dist)
            self.perform_action()

        # self.predict_next_actions()
        # print("Predicted Actions:")
        # print(self._possible_actions)

        # log footer of logging file
        self.env.finish_experiment()

    def perform_action(self):
        position_before_action = tuple(self.env.agent_pos)

        # print("Position")
        # print(position_before_action)
        # print("Facing")
        # print(self.env.facing_direction)
        # print("Actions")
        # print(self._possible_actions)

        if len(self._possible_actions) < 1:
            self.go_back()
            self
        else:
            # print(self._possible_actions)
            action = self._possible_actions[np.random.randint(
                0, high=len(self._possible_actions))]
            # print(action)

            match action:
                case (-1, 0):
                    self.go_forward()
                case (0, -1):
                    self.go_left()
                case (0, 1):
                    self.go_right()
                case (1, 0):
                    self.go_back()
                case _:
                    print("Impossible Action: " + action)
        #print("Position after:")
        # print(self.env.agent_pos)
        # if(self.env.agent_pos == position_before_action):
        #     print("Not Moved")

    # Get passable tiles from the current tile by turning arround and looking at the tile in front.

    def get_surroundings(self):
        # Since I want the movement to be relative to the facing direction
        # I need to save use the Rotation matrix weirdly
        save_rot = self.rotation_matrix.copy()
        self.rotation_matrix = np.array([[1, 0], [0, 1]])
        for i in range(4):
            cone = self.env.get_view_cone(relative=True)
            # print(cone.keys())

            if(cone[(-1, 0)].passable):
                self._possible_actions.append(
                    tuple(np.matmul(self.rotation_matrix, NORTH)))
            self.turn_right()

        self.rotation_matrix = save_rot.copy()
        save_rot = None
        # print("Directions:")
        # print(np.matmul(self.rotation_matrix,[-1,0]))
        # print(self.env.facing_direction)

    # Gets the actions that are possible from the Tile right in front of the one of the agent

    def predict_next_actions(self):
        self._possible_actions = []
        # print(self.env.agent_pos)
        # print(self.env.facing_direction)
        cone = self.env.get_view_cone(relative=True)
        # print(cone.keys())
        for tile in [(-1, -1), (-2, 0), (-1, 1)]:
            if((tile in cone.keys()) and cone[tile].passable):
                possible_action = np.array(tile)
                possible_action[0] += 1
                # self._possible_actions.append(tuple(np.matmul(self.rotation_matrix,possible_action)))

                self._possible_actions.append(tuple(possible_action))

    def turn_left(self):
        self.env.perform_action(action=ACTION_MAPPING["TURN LEFT"], agent=self)
        self.rotation_matrix = np.matmul(
            np.array([[0, -1], [1, 0]]), self.rotation_matrix)

    def turn_right(self):
        self.env.perform_action(
            action=ACTION_MAPPING["TURN RIGHT"], agent=self)
        self.rotation_matrix = np.matmul(
            np.array([[0, 1], [-1, 0]]), self.rotation_matrix)

    def turn_back(self):
        self.env.perform_action(
            action=ACTION_MAPPING["TURN RIGHT"], agent=self)
        self.env.perform_action(
            action=ACTION_MAPPING["TURN RIGHT"], agent=self)
        self.rotation_matrix = np.matmul(
            np.array([[-1, 0], [0, -1]]), self.rotation_matrix)

    def go_left(self):
        self.turn_left()
        self.predict_next_actions()
        self.env.perform_action(action=tuple(
            np.matmul(self.rotation_matrix, NORTH)), agent=self)

    def go_right(self):
        self.turn_right()
        self.predict_next_actions()
        self.env.perform_action(action=tuple(
            np.matmul(self.rotation_matrix, NORTH)), agent=self)

    def go_back(self):
        self.turn_back()
        self.predict_next_actions()
        self.env.perform_action(action=tuple(
            np.matmul(self.rotation_matrix, NORTH)), agent=self)

    def go_forward(self):
        self.predict_next_actions()
        self.env.perform_action(action=tuple(
            np.matmul(self.rotation_matrix, NORTH)), agent=self)
