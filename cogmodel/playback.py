#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 1 15:36:04 2017
    Simple agent which replays the actions recorded during the 
    webblocks experiment.
@author: jpoeppel
"""

import datetime, time
import os, threading
from ast import literal_eval

from .gridEnvironment import GridEnvironment
from .gridEnvironment import NORTH, SOUTH, EAST, WEST, TURN_RIGHT, TURN_LEFT

CONDITION_PATH = os.path.abspath(os.path.dirname(__file__)) + os.path.sep + "Conditions"

# Global memory to speed up parsing for subsequent occurances of the same
# condition.
env_store = {}

ACTION_MAPPING = {"Left": WEST, "Right": EAST, "Up": NORTH, 
              "Down": SOUTH, "Left": TURN_LEFT,
              "Right": TURN_RIGHT,
              "NORTH": NORTH, "SOUTH": SOUTH, "EAST": EAST,
              "TURN LEFT": TURN_LEFT, "TURN RIGHT": TURN_RIGHT,
              "WEST": WEST}

def crawl_results(path, use_caching=False):
    """
        Collects and reads in all the recorded participant behaviour at the 
        given root path.

        Parameters
        ----------
        path: str
            The root path where to find the participant recordings.
        use_caching: bool (default= True)
            If true, will reuse already loaded environments, which may already
            include precomputed distances, greatly speeding up later calls,
            but might invalidate timing analysis.

        Returns
        -------
            dict
            A dictionary containing a list of tuples for each recorded run 
            found under the given path of the condition specified by the key,
            each containing the information provided by load_experiment. 
    """
    users = [e for e in os.listdir(path) 
                        if os.path.isdir(path + os.path.sep +e)]
    conditions = {}
    skipped = []
    num_completed = 0
    for u in users:
        files = os.listdir(path + os.path.sep +u)
        for f in files:
            if "condMap" in f:
                try:
                    exp = load_experiment(path + os.path.sep +u + os.path.sep + f, 
                                                                    use_caching)
                    if exp[0] is not None:
                        conditions[f].append(exp)
                        num_completed += 1
                    else: 
                        skipped.append(u + os.path.sep + f)
                except KeyError:
                    conditions[f] = [load_experiment(path + os.path.sep 
                                                        + u + os.path.sep + f,
                                                        use_caching)]
                    num_completed += 1
                except IndexError:
                    #Ignore bad files
                    pass
                
    print("Skipped: {} runs because they were incomplete.".format(len(skipped)))
    print("Total number of runs: {}".format(num_completed))
    return conditions


def load_experiment(path, use_caching=True):
    """
        Small function which reads in an experimental result and constructs
        the environment as well as the playback agent from it.

        Parameters
        ----------
        path: str
            The path for the recorded run.
        use_caching: bool (default= True)
            If true, will reuse already loaded environments, which may already
            include precomputed distances, greatly speeding up later calls,
            but might invalidate timing analysis.

        Returns
        -------
            environment: blockworld.Environment
                An environment object corresponding to the world of the 
                experiment.
            targets: dict
                A dictionary containing information for each potential target
                within the environment and condition, with positions as keys.
            playback_agent : PlaybackAgent
                An instance of a PlaybackAgent which can be used to reproduce
                the recorded behaviour.
            goal_pos: tuple
                The position of the true goal for the recorded condition.

    """
    with open(path, "r") as condition:
        lines = condition.readlines()
        condition_end = lines.index("\n")
        
    for i, line in enumerate(lines[:condition_end]):
        if "EnvString" in line:
            start = i+1
        if "AlwaysVisibles" in line:
            end = i
            break
        
    env_string = "".join(lines[start:end]).strip()
    if not use_caching or env_string not in env_store:
        env_store[env_string] = GridEnvironment(env_string)
    environment = env_store[env_string]
    start_pos = literal_eval(lines[condition_end-1].split(":")[1].strip())

    # Fix orientation, old model counted top to bottom!
    start_pos = (start_pos[0], start_pos[1])

    agent_id = os.path.basename(os.path.dirname(path)) 
    playback_agent = PlaybackAgent(agent_id,
                                  lines[condition_end+1:], 
                                  start_pos=start_pos,  
                                  environment=environment)
    
    goal = literal_eval(lines[condition_end-2].strip("Goal:").strip())
    # Determine possible goals. Required since C1 and C3 do not store all
    # targets in their files:
    condID = os.path.basename(os.path.normpath(path))
    cond2ID = condID.split("_")[0] + "_C2_" + condID.split("_")[-1]

    try:
        # Loading all targets from condition file
        with open(CONDITION_PATH + os.path.sep + cond2ID, "r") as condition2:
            for line in condition2:
                if "Targets:" in line:
                    targets = literal_eval(line[line.find("{"):])
                    break
    except IOError:
        # Use the targets specified in this file when the condition 2 file
        # cannot be found, e.g. when this is a custom file
        for line in lines:
            if "Targets:" in line:
                targets = literal_eval(line[line.find("{"):])
                break
            
    return environment, targets, playback_agent, goal["target"]
        


class PlaybackAgent(object):
    """
        Simple playback agent which will reproduce the recorded actions
        of the participants.

        Parameters
        ----------
        agent_id: str/int
            The identifier for the agent.
        action_rows: str
            The string containing all the performed actions that were 
            recorded.
        start_pos: tuple 
            The agent's starting position.
        environment: cogmodel.GridEnvironment
            A reference to the environment object corresponding to the world
            the actions were recorded in.

        Attributes
        ----------
        id: str/int
            The agent_id passed in as the first argument.
        actions: list
            A list of tuples for all the actions that have been recorded in the 
            file. See ``_parse_actions`` for more information.
        environment: cogmodel.GridEnvironment
            The passed environment object.
        cur_idx: int
            A counter for the next action which should be replayed.
    """
    
    def __init__(self, agent_id, action_rows, start_pos, environment):
        self.id = agent_id
        try:
            self.actions = self._parse_actions(action_rows)
        except IndexError:
            raise IndexError("Error parsing actions of user: {}".format(agent_id))
        self.environment = environment
        self.cur_idx = 0
        self.environment.initialize_agent(start_pos)
    
    def _parse_actions(self, action_rows):
        """
            Private function to parse the action recordings.

            Parameters
            ----------
            action_rows: str
                The string containing all the performed actions that were 
                recorded.

            Returns
            -------
                list
                A list of tuples containing, the timestamp of the action and
                the action string.
        """
        res = []
        date_split = action_rows[0].find(": ")-1
        for row in action_rows:
            if row != "":
                res.append((datetime.datetime.strptime(row[:date_split], 
                                                       "%Y-%m-%d %H:%M:%S.%f"), 
                            row[date_split+3:].strip()))
        return res
        
    def perform_action(self, ignore_duds=False):
        """
            Trigger the agent to perform the next action.

            Parameters
            ----------
            ignore_dus: bool (default=False)
                If true, actions not changing the agent's position, will be
                skipped.

            Returns
            -------
                tuple
                The new position after performing the action or none, if there
                are no more actions in the recording.
        """
        try:
            action = self.actions[self.cur_idx]
        except IndexError:
            print("Agent {} finished it's episode.".format(self.id))
            return None 
        if not "Finished" in action[1]:
            _, action_string = action[1].split("-")

            action = ACTION_MAPPING[action_string]

            new_pos = self.environment.perform_action(action)

        else: #Condition was finished
            return None
        
        self.cur_idx += 1
        return new_pos


    def replay(self, callback, speedup=1):
        """
            Function allowing to replay the interaction in (modified) real-time.
            Will run a while loop until the end of the recording is reached and
            call the provided callback function at each tick.

            Parameters
            ---------
            callback: callable
                A function which will be called with the new position after each
                step. Can be used to update renderes
            speedup: int, optional (Default: 1)
                A speedup factor. The time delta between two 
                actions will be divided by this factor.
        """
        
        while True:
            if self.cur_idx == len(self.actions):
                break
            cur_timestamp = self.actions[self.cur_idx][0]
            last_timestamp = self.actions[self.cur_idx-1][0] if self.cur_idx > 0 else cur_timestamp
            delta = (cur_timestamp - last_timestamp)/speedup
            time.sleep(delta.total_seconds())
            new_pos = self.perform_action()
            if new_pos is None:
                break
            callback(new_pos)
