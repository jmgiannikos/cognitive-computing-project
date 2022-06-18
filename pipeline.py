import argparse
from json import load
from operator import length_hint
from turtle import position
import numpy as np
import pandas as pd
import dataframe_image as dfi
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import seaborn as sns
from ast import literal_eval
from cogmodel.gridEnvironment import GridEnvironment, NORTH, SOUTH, WEST, EAST
from cogmodel import renderer
from cogmodel import playback
from cogmodel.Agents.tremaux import tremaux
from cogmodel.Agents.wallFollower import wallFollower
from cogmodel.Agents.greedy_simple import greedy
from cogmodel.Agents.directedTremaux import directedTremaux
from cogmodel.Agents.simple import simple
from cogmodel import log

VIEW_RADIUS = 5


class pipeline(object):

    def __init__(self, args):
        self.agent_types = args.agent  # list of names of to be used agents
        self.playback = args.playback  # file path to .txt file containing playback
        self.labyrinth = args.labyrinth  # file path to .txt file containing labyrinths
        self.times = max(el for el in [args.times, 1] if el is not None)
        self.envs = []  # list of all grid environments

    def run(self):
        """
            Runs and controls pipeline
        """

        if self.agent_types:
            # setting up logging for "master file"
            master_path = "data/Agent_data/overall_averages.csv"
            header_string = "labID,agentID,totalActions,totalActionValue,totalMoves,totalTurns,totalNorth,totalEast,totalSouth," + \
                            "totalWest,totalLeft,totalRight,totalTime,timePerAction,pathlength,totalVisitedGround,percVisitedGround," + \
                            "minCogLoad,maxCogLoad,avCogLoad,startCogLoad,endCogLoad"  # ,labTime,labValue"
            log(master_path, header_string)
            # constricting environments, can be used for all runs if reset properly
            self._construct_envs()
            for env in self.envs:
                # going over all agents that should be run
                for agent_type in self.agent_types:
                    match agent_type:
                        case "wall_follower":
                            for i in range(0, self.times):
                                # setting log path of env
                                log_path = "data/Agent_data/" + \
                                    env.name + "_" + str(agent_type) + \
                                    "/" + str(i) + "/logging.txt"
                                env.set_logging(
                                    path=log_path, agent_type=agent_type)
                                # constructing agent and running it on env
                                agent = wallFollower(env)
                                agent.run()
                                # resetting env
                                env.reset()
                            self._save_logging_info(env.name, str(agent_type))
                        case "greedy:
                            for i in range(0, self.times):
                                # setting log path of env
                                log_path = "data/Agent_data/" + \
                                    env.name + "_" + str(agent_type) + \
                                    "/" + str(i) + "/logging.txt"
                                env.set_logging(
                                    path=log_path, agent_type=agent_type)
                                # constructing agent and running it on env
                                agent = greedy(env)
                                agent.run()
                                # resetting env
                                env.reset()
                            self._save_logging_info(env.name, str(agent_type))
                        case "tremaux":
                            # running agent on env self.times times
                            for i in range(0, self.times):
                                # setting log path of env
                                log_path = "data/Agent_data/" + \
                                    env.name + "_" + str(agent_type) + \
                                    "/" + str(i) + "/logging.txt"
                                env.set_logging(
                                    path=log_path, agent_type=agent_type)
                                # constructing agent and running it on env
                                agent = tremaux(env)
                                agent.run()
                                # resetting env
                                env.reset()
                            self._save_logging_info(env.name, str(agent_type))
                        case "directedTremaux":
                            # running agent on env self.times times
                            for i in range(0, self.times):
                                # setting log path of env
                                log_path = "data/Agent_data/" + \
                                    env.name + "_" + str(agent_type) + \
                                    "/" + str(i) + "/logging.txt"
                                env.set_logging(
                                    path=log_path, agent_type=agent_type)
                                # constructing agent and running it on env
                                agent = directedTremaux(env)
                                agent.run()
                                # resetting env
                                env.reset()
                            self._save_logging_info(env.name, str(agent_type))
                        case "simple":
                            print("Ahh")
                            # running agent on env self.times times
                            for i in range(0, self.times):
                                # setting log path of env
                                log_path = "data/Agent_data/" + \
                                    env.name + "_" + str(agent_type) + \
                                    "/" + str(i) + "/logging.txt"
                                env.set_logging(
                                    path=log_path, agent_type=agent_type)
                                # constructing agent and running it on env
                                agent = simple(env)
                                agent.run()
                                # resetting env
                                env.reset()
                            self._save_logging_info(env.name, str(agent_type))
        elif self.playback:
            self._playback()
        elif self.graph:
            self._draw_graphs()
        else:
            print(
                "You either have to use an agent via '-a' or a playback file via '-p'!")
            return -1

    def _construct_envs(self):
        """
            Reads labyrinth(s) from .txt file and creates fitting environments
        """

        def _add_env(self):
            """
                Initializes gridEnvs and adds them to envs list
            """
            env = GridEnvironment(target=goal_position, initial_agent_pos=start_position,
                                  view_radius=VIEW_RADIUS, name=name, env_string=env_string, facing=facing)
            self.envs.append(env)

        # information used to generate environment
        env_string = ""
        start_position = ()
        goal_position = ()
        facing = ""
        name = ""

        # use user labyrinth if given
        if self.labyrinth:

            # opening and reading file
            with open(args.labyrinth) as file:
                read_point = 0
                while(line := file.readline()):
                    if line in ["EnvString:\n", "Goal:\n", "Start:\n", "Facing:\n", "Name:\n"]:
                        read_point += 1
                    else:
                        match read_point:
                            case 1:
                                env_string += line
                            case 2:
                                goal_position = literal_eval(line.strip())
                            case 3:
                                start_position = literal_eval(line.strip())
                            case 4:
                                facing = literal_eval(line.strip())
                            case 5:
                                env_string = env_string.strip()
                                name = line.strip()
                                _add_env(self)
                                read_point = 0
                                env_string = ""
                                start_position = ()
                                goal_position = ()
                                facing = ""
                                name = ""
                            case _:
                                print(
                                    "Something went wrong while trying to read the labyrinth file.")
                                return -1

            # closing file
            file.close()
        else:  # use default labyrinth
            env_string = "##############################\n" + \
                "#gg###g#ggggg#ggg#gggggggggg##\n" + \
                "##gggggg##g#g###ggg#g##g#g#gg#\n" + \
                "#g#g#g###gg#g#ggg####gg###g#g#\n" + \
                "#gg##ggg#g#gg#g##gg###g###gg##\n" + \
                "##g##g#g##gg#ggg#g#g#gggg#g#g#\n" + \
                "##ggggg#ggg##g##gggggg##ggggg#\n" + \
                "#g##g#g#g#gg#gggg######gg##g##\n" + \
                "#g###ggg#gg#gg########gg#gg###\n" + \
                "#gg#gg#gg#gg#ggggggg##g#g#gg##\n" + \
                "##gg##g#gg#ggg#g#g#ggg##gg#gg#\n" + \
                "###ggggg#g###gg#gg#g#g###g##g#\n" + \
                "##gg###gggggg#g##gg#gg##ggggg#\n" + \
                "#gg#ggg#####g#g##g#g#gggg#g#g#\n" + \
                "#g#gg#gggg#ggggg#g#g#g#g##gg##\n" + \
                "##gg###g#ggg#g#g##ggg##gg#g#g#\n" + \
                "#g##g#ggg#g##gg###g#g###g##gg#\n" + \
                "#g#ggg###g#ggg#ggggg#ggg#ggg##\n" + \
                "#ggg#ggggggg#ggg#g#ggg#g#g##g#\n" + \
                "##g#g#g#g#g#gg##ggg#g#g#ggg#g#\n" + \
                "#gg#ggg##gg#g##g###g##ggg#g#g#\n" + \
                "####g#g###g#ggggggggggg##gggg#\n" + \
                "#gggg##gggg#####g#g##g#gg###g#\n" + \
                "#g#g#ggg##ggggg#gg#g#gg#ggg#g#\n" + \
                "#gg#gg#g##g#g#gg#ggg##ggg#g###\n" + \
                "###g#g##ggg#g#g##g##ggg###ggg#\n" + \
                "###gg#g###g#g#gg#g##g#g#gg##g#\n" + \
                "##g#g#ggggg#gg#g#ggg##g##g#g##\n" + \
                "#gggggg#g#gg#g#g#g#gg#ggggggg#\n" + \
                "##############################"
            start_position = (28, 1)
            goal_position = (3, 28)
            facing = (0, 1)
            name = "Default_Labyrinth"
            _add_env(self)

    def _save_logging_info(self, labID, agentID):
        """
            Goes over logging files and add save information as graphs and in .csv file.
            Also saves average in same .csv file and in "Master" .csv file

            Parameters
            ----------
            labID: str
                The name of the labyrinth for which information will get saved. Need to determine path names.
            agentID: str
                The name of the strategy for which information will get saved. Need to determine path names.
        """

        # save header for .csv file
        csv_path = "data/Agent_data/" + \
            labID + "_" + agentID + \
            "/evaluation.csv"
        master_path = "data/Agent_data/overall_averages.csv"
        header_string = "ID,labID,agentID,totalActions,totalActionValue,totalMoves,totalTurns,totalNorth,totalEast,totalSouth," + \
            "totalWest,totalLeft,totalRight,totalTime,timePerAction,pathlength,totalVisitedGround,percVisitedGround," + \
            "minCogLoad,maxCogLoad,avCogLoad,startCogLoad,endCogLoad"  # ,labTime,labValue"
        log(csv_path, msg=header_string)

        # used to save values for all i iterations so averages can be calculated
        totalActions = []
        totalActionValue = []
        totalMoves = []
        totalTurns = []
        totalNorth = []
        totalEast = []
        totalSouth = []
        totalWest = []
        totalLeft = []
        totalRight = []
        totalTime = []
        totalTimePerAction = []
        pathlength = []
        totalVisitedGround = []
        percVisitedGround = []
        minCogLoad = []
        maxCogLoad = []
        avCogLoad = []
        startCogLoad = []
        endCogLoad = []

        # going over all log files that belong to labID + agentID combination
        for number in range(0, self.times):
            # path where file can be found
            log_path = "data/Agent_data/" + \
                labID + "_" + agentID + \
                "/" + str(number) + "/logging.txt"
            # path where graphs should be saved
            save_path = "data/Agent_data/" + \
                labID + "_" + agentID + \
                "/" + str(number)
            # reading log file and saving important metrics
            action_types = []
            positions = []
            time = []
            load = []
            length = []
            action_values = []
            lab = []

            action_types, positions, time, load, length, action_values, lab = self._read_logging(
                path=log_path)

            # --- PREPARING DATA FOR PLOTS ---
            # getting information about action types
            overall_actions = len(action_types)
            totalActions.append(overall_actions)
            unique, counts = np.unique(action_types, return_counts=True)
            action_dict = dict(zip(unique, counts))
            move_number = action_dict.get(
                'NORTH') + action_dict.get('EAST') + action_dict.get('SOUTH') + action_dict.get('WEST')
            totalMoves.append(move_number)
            turn_number = action_dict.get(
                'TURN LEFT') + action_dict.get('TURN RIGHT')
            totalTurns.append(turn_number)
            north_number = action_dict.get('NORTH')
            totalNorth.append(north_number)
            east_number = action_dict.get('EAST')
            totalEast.append(east_number)
            south_number = action_dict.get('SOUTH')
            totalSouth.append(south_number)
            west_number = action_dict.get('WEST')
            totalWest.append(west_number)
            left_number = action_dict.get('TURN LEFT')
            totalLeft.append(left_number)
            right_number = action_dict.get('TURN RIGHT')
            totalRight.append(right_number)

            # getting time information
            acc_time = np.cumsum(time)
            time_total = acc_time[-1]/1000000  # milliseconds
            totalTime.append(time_total)
            time_per_action = time_total/overall_actions  # milliseconds
            totalTimePerAction.append(time_per_action)

            # getting action information
            unique_data = [list(x) for x in set(tuple(x) for x in positions)]
            visited_total = len(unique_data)
            totalVisitedGround.append(visited_total)
            path_length = length[-1]
            pathlength.append(path_length)

            # getting total action value
            total_action_value = np.cumsum(action_values)[-1]
            totalActionValue.append(total_action_value)

            # getting load information
            min_load = load.min()
            minCogLoad.append(min_load)
            max_load = load.max()
            maxCogLoad.append(max_load)
            av_load = np.mean(load)
            avCogLoad.append(av_load)
            start_load = load[0]
            startCogLoad.append(start_load)
            end_load = load[-1]
            endCogLoad.append(end_load)

            # preparing labyrinth into dict with time and into dict with visited value
            lab_time = dict()
            lab_value = dict()
            number_walls = 0
            number_non_walls = 0
            for i in range(0, len(lab)):
                for j in range(0, len(lab[i])):
                    if lab[i][j] == '#':
                        lab_time[(i, j)] = -1
                        lab_value[(i, j)] = -1
                        number_walls += 1
                    else:
                        lab_time[(i, j)] = 0
                        lab_value[(i, j)] = 0
                        number_non_walls += 1
            for i in range(0, len(positions)):
                lab_value[tuple(positions[i])] += 1
                lab_time[tuple(positions[i])] += time[i] / \
                    1000000  # milliseconds

            visited_perc = visited_total/number_non_walls
            percVisitedGround.append(visited_perc)

            # --- PLOTS ---
            # Heatmap action-amount per ground tile and time per ground tile
            ser = pd.Series(list(lab_value.values()),
                            index=pd.MultiIndex.from_tuples(lab_value.keys()))
            df = ser.unstack().fillna(0)
            ser = pd.Series(list(lab_time.values()),
                            index=pd.MultiIndex.from_tuples(lab_time.keys()))
            df2 = ser.unstack().fillna(0)
            fig, ax = plt.subplots(1, 2, figsize=(25, 10))
            plt1 = sns.heatmap(df, vmin=-1, vmax=max(lab_value.values()),
                               cmap="Blues", ax=ax[0], cbar_kws={'label': 'Number of visits'})
            plt1.collections[0].colorbar.set_label("Visit amount on tile")
            plt1.collections[0].colorbar.ax.tick_params(labelsize=15)
            plt1.figure.axes[-1].yaxis.label.set_size(20)
            plt1.xaxis.tick_top()
            plt2 = sns.heatmap(df2, vmin=-1, vmax=max(lab_time.values()),
                               cmap="Blues", norm=LogNorm(), ax=ax[1])
            plt2.collections[0].colorbar.set_label("Time on tile in ms")
            plt2.xaxis.tick_top()
            plt2.collections[0].colorbar.ax.tick_params(labelsize=15)
            plt2.figure.axes[-1].yaxis.label.set_size(20)
            ax[0].set_title('Number of actions on tile',
                            fontsize=25, fontweight="bold", y=1.08)
            ax[1].set_title('Time on tile', fontsize=25,
                            fontweight="bold", y=1.08)

            fig.figure.savefig(save_path + '/heatmaps.png')

            # Action types table
            df = pd.DataFrame([['TOTAL', overall_actions],
                               ["Total moves", move_number],
                               ["Total turns", turn_number],
                               ['North', north_number],
                               ['East', east_number],
                               ['South', south_number],
                               ['West', west_number],
                               ["Turn left", left_number],
                               ["Turn right", right_number]],
                              columns=['Action type', 'Amount'])

            df = df.style.set_table_styles([
                {
                    "selector": "thead",
                    "props": "background-color:whitesmoke; border-top: 2 px solid black;"
                },
                {
                    "selector": ".row0, .row2, .row6",
                    "props": "border-bottom: 2px solid black"
                }
            ]).background_gradient().hide_index()
            dfi.export(df, save_path + '/action_types.png')

            # Cognitive load table
            df = pd.DataFrame.from_dict({'Minimal cognitive load': min_load,
                                        "Maximal cognitive load": max_load,
                                         "Average cognitive load": av_load,
                                         'Cognitive load start': start_load,
                                         'Cognitive load end': end_load}, orient="index")

            df = df.style.set_table_styles([
                {
                    "selector": "thead",
                    "props": "display:none"
                },
                {
                    "selector": ".row2",
                    "props": "border-bottom: 2px solid black"
                },
                {"selector": "tbody td", "props": "border-left: 1px solid black"},
            ]).highlight_max(color='#63a2cb')
            dfi.export(df, save_path + '/cognitive_load.png')

            # General information table
            df = pd.DataFrame.from_dict({'Time in total': '{:,.5} ms'.format(time_total),
                                        "Actions in total": overall_actions,
                                         "Action value in total": total_action_value,
                                         "Time per action": '{:,.3} ms'.format(time_per_action),
                                         'Path length': path_length,
                                         'Visited ground tiles in total': visited_total,
                                         'Percentage of visited ground tiles': '{:,.2%}'.format(visited_perc)}, orient="index")

            df = df.style.set_table_styles([
                {
                    "selector": "thead",
                    "props": "display:none"
                },
                {
                    "selector": ".row3",
                    "props": "border-bottom: 2px solid black"
                },
                {"selector": "tbody td", "props": "border-left: 1px solid black"},
            ])
            dfi.export(df, save_path + '/general_information.png')

            # --- SAVING INFORMATION IN .CSV FILE ---
            information_string = str(number) + ',' + labID + ',' + agentID + ',' + str(overall_actions) + ',' + str(total_action_value) + ',' + str(move_number) + ',' + str(turn_number) + ',' + str(north_number) + ',' + \
                str(east_number) + ',' + str(south_number) + ',' + str(west_number) + ',' + str(left_number) + ',' + str(right_number) + ',' + str(time_total) + ',' + \
                str(time_per_action) + ',' + str(path_length) + ',' + str(visited_total) + ',' + str(visited_perc) + ',' + str(min_load) + ',' + str(max_load) + ',' + \
                str(av_load) + ',' + str(start_load) + ',' + \
                str(end_load)  # + ',' + str(lab_time) + ',' + str(lab_value)
            log(csv_path, msg=information_string)

        # --- CALCULATING AVERAGE AND SAVING IT ---
        # used to save values for all i iterations so averages can be calculated
        totalActions = np.mean(totalActions)
        totalActionValue = np.mean(totalActionValue)
        totalMoves = np.mean(totalMoves)
        totalTurns = np.mean(totalTurns)
        totalNorth = np.mean(totalNorth)
        totalEast = np.mean(totalEast)
        totalSouth = np.mean(totalSouth)
        totalWest = np.mean(totalWest)
        totalLeft = np.mean(totalLeft)
        totalRight = np.mean(totalRight)
        totalTime = np.mean(totalTime)
        totalTimePerAction = np.mean(totalTimePerAction)
        pathlength = np.mean(pathlength)
        totalVisitedGround = np.mean(totalVisitedGround)
        percVisitedGround = np.mean(percVisitedGround)
        minCogLoad = np.mean(minCogLoad)
        maxCogLoad = np.mean(maxCogLoad)
        avCogLoad = np.mean(avCogLoad)
        startCogLoad = np.mean(startCogLoad)
        endCogLoad = np.mean(endCogLoad)

        information_string = str(self.times) + ',' + labID + ',' + 'AVERAGE' + ',' + str(totalActions) + ',' + str(totalActionValue) + ',' + str(totalMoves) + ',' + str(totalTurns) + ',' + str(totalNorth) + ',' + str(totalEast) + ',' + str(totalSouth) + ',' + str(totalWest) + ',' + str(totalLeft) + ',' + str(
            totalRight) + ',' + str(totalTime) + ',' + str(totalTimePerAction) + ',' + str(pathlength) + ',' + str(totalVisitedGround) + ',' + str(percVisitedGround) + ',' + str(minCogLoad) + ',' + str(maxCogLoad) + ',' + str(avCogLoad) + ',' + str(startCogLoad) + ',' + str(endCogLoad)  # + ',' + str(lab_time) + ',' + str(lab_value)
        log(csv_path, msg=information_string)

        information_string = labID + ',' + agentID + ',' + str(totalActions) + ',' + str(totalActionValue) + ',' + str(totalMoves) + ',' + str(totalTurns) + ',' + str(totalNorth) + ',' + str(totalEast) + ',' + str(totalSouth) + ',' + str(totalWest) + ',' + str(totalLeft) + ',' + str(
            totalRight) + ',' + str(totalTime) + ',' + str(totalTimePerAction) + ',' + str(pathlength) + ',' + str(totalVisitedGround) + ',' + str(percVisitedGround) + ',' + str(minCogLoad) + ',' + str(maxCogLoad) + ',' + str(avCogLoad) + ',' + str(startCogLoad) + ',' + str(endCogLoad)  # + ',' + str(lab_time) + ',' + str(lab_value)
        log(master_path, msg=information_string)

    def _read_logging(self, path):
        """
            Reads logging information from logfile given by path.

        Parameters
        ---------------------------------------------------------------------------------
        path: str
           Place where log file is saved.

        Returns
        ---------------------------------------------------------------------------------
        action_types: list(String)
            List containing all actions taken after each other. Eg ['NORTH', 'EAST']
        positions: list((int,int))
            List of positions agent visited after each other
        time: list(int)
            List of times agent took in step i. (in nano seconds)
        load: list(int)
            List of cognitive loads agent had at step i.
        length: list(int)
            List of pathlengths at time i.            
        action_values: list(float)
            List of action values at step i.
        lab: list(String)
            List containing strings of labyrinth rows. String at i is labyrinth row i.s    
        """
        action_types = []
        positions = []
        time = []
        load = []
        length = []
        action_values = []
        lab = []
        # opening and reading file
        with open(path) as file:
            read_point = 0
            while(line := file.readline()):
                if line in ["EnvString:\n", "Goal:\n", "Position:\n", "Time:\n", "Load:\n", "Length:\n", "Action:\n"]:
                    read_point += 1
                elif "Condition starting" in line:
                    read_point += 1
                elif "Condition finished" in line:
                    file.readline()
                else:
                    match read_point:
                        case 0:
                            continue
                        case 1:
                            lab.append(line.strip())
                        case 2:
                            continue
                        case 3:
                            date_split = line.find(": ")+2
                            action_types.append(line[date_split:].strip())
                        case 4:
                            positions = np.array(literal_eval(line.strip()))
                        case 5:
                            time = np.array(literal_eval(line.strip()))
                        case 6:
                            load = np.array(literal_eval(line.strip()))
                        case 7:
                            length = np.array(literal_eval(line.strip()))
                        case 8:
                            action_values = np.array(
                                literal_eval(line.strip()))
                        case _:
                            print(
                                "Something went wrong while trying to read the log file.")
                            return -1

        # closing file
        file.close()
        # returning info
        return action_types, positions, time, load, length, action_values, lab

    def _playback(self):
        """
            Play backs logging file given by user.
        """

        # --- SET-UP ---
        # reading in information to construct playback agent
        env_string = ""
        action_rows = []
        # not the most elegant way, but works I guess
        with open(args.playback) as file:
            read_point = 0
            while(line := file.readline()):
                if line in ["EnvString:\n", "Goal:\n", "StartPosition:\n", "Facing:\n", "Name:\n", "AgentType:\n"]:
                    read_point += 1
                elif "Condition starting" in line:
                    action_rows.append(line)
                    read_point += 1
                elif "Condition finished" in line:
                    action_rows.append(line)
                    break
                else:
                    match read_point:
                        case 0:
                            continue
                        case 1:
                            env_string += line
                        case 2:
                            goal_position = literal_eval(line.strip())
                        case 3:
                            start_position = literal_eval(line.strip())
                        case 4:
                            facing = literal_eval(line.strip())
                        case 5:
                            name = line.strip()
                        case 6:
                            agent_type = line.strip()
                        case 7:
                            action_rows.append(line)
                        case 8:
                            break
                        case _:
                            print(
                                "Something went wrong while trying to read the labyrinth file.")
                            return -1

        # closing file
        file.close()

        # --- PLAYBACK ---
        if renderer.pygame_available:
            rend = renderer.PygameRenderer()
        else:
            rend = renderer.MatplotlibRenderer()

        # TODO check if envString still works with real log files
        env = GridEnvironment(target=goal_position, initial_agent_pos=start_position,
                              view_radius=VIEW_RADIUS, env_string=env_string[:-1], facing=facing)
        playback_agent = playback.PlaybackAgent(
            agent_id=agent_type, action_rows=action_rows, start_pos=start_position, environment=env)

        rend.plot(grid=env.get_view_cone(playback=True), agent=env.agent_pos,
                  facing=env.facing_direction, show_trajectory=True)

        def my_callback(pos):
            rend.plot(grid=env.get_view_cone(playback=True), agent=pos,
                      facing=env.facing_direction, show_trajectory=True)
            # To allow for event handling and matplotlib updates
            rend.pause(0.001)

        playback_agent.replay(my_callback, speedup=1)

        renderer.show()


if __name__ == "__main__":
    """
        Main method of the pipeline
        ---------------------------
        Parses command line arguments and starts pipeline
        Use "pipeline.py -h" or "pipeline.py -help" or read the documentation to see what command line arguments are available.
    """

    # --- ARGUMENT PARSER ---
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    # pipeline either creates new agents or does playback, not both at once
    # TODO: add agents names once available
    group.add_argument(
        "-a", "--agent", help="name of the agent that should be used", choices=['wall_follower', 'tremaux', 'directedTremaux','simple', 'greedy'], nargs="+")
    group.add_argument(
        "-p", "--playback", help="file path to .txt file containing log-file that should be replayed")
    parser.add_argument(
        "-t", "--times", help="determines how often agent shall run on labyrinth. Graph data will be generated over average values.", type=int)
    # if -l is used for playback or graph generation only graphs are saved!
    parser.add_argument(
        "-l", "--labyrinth", help=" file path to .txt file containing to be used labyrinth(s)")
    # parsing arguments
    args = parser.parse_args()

    # --- PIPELINE START ---
    pipe = pipeline(args)
    pipe.run()
