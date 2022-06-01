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
from cogmodel.Agents.directedTremaux import directedTremaux

VIEW_RADIUS = 5


class pipeline(object):

    def __init__(self, args):
        self.agent_types = args.agent  # list of names of to be used agents
        self.agent_type = ""  # current agent_type
        self.playback = args.playback  # file path to .txt file containing playback
        # file path to .txt file containing log information for which graphs should be generated
        self.graph = args.graph
        self.labyrinth = args.labyrinth  # file path to .txt file containing labyrinths
        self.log = args.logging  # bool, toggles logging of results
        self.show = args.show  # bool, toggles showing of results
        self.envs = []  # list of all grid environments

    def run(self):
        """
            Runs and controls pipeline
        """

        if self.agent_types:
            # TODO add other available agents
            for agent_type in self.agent_types:
                self.agent_type = agent_type
                # constructing grid environment(s)
                self.envs = []
                self._construct_envs()
                match agent_type:
                    case "wall_follower":
                        # TODO make agent once available
                        for env in self.envs:
                            print("Constructing agent")

                    case "tremaux":
                        for env in self.envs:
                            agent = tremaux(env, self.log)
                            agent.run()
                            # TODO: add graphs if wanted here
                    case "directedTremaux":
                        for env in self.envs:
                            agent = directedTremaux(env, self.log)
                            agent.run()

        elif self.playback:
            self._playback()
        elif self.graph:
            self._draw_graphs()
        else:
            print(
                "You either have to use an agent via '-a', a playback file via '-p' or a log file via '-g'!")
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
                                  view_radius=VIEW_RADIUS, env_string=env_string, facing=facing)
            if self.log:
                # ATTTENTION: If same logging path is used twice (eg by starting pipeline with same arguments twice) logging file will get corrupted! Always delete or rename folders manually!
                log_path = "data/Agent_data/" + \
                    str(name) + "_" + str(self.agent_type) + "/logging_" + \
                    str(name) + "_" + str(self.agent_type)
                env.set_logging(path=log_path, env_name=name,
                                agent_type=self.agent_type)
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
                                start_position = literal_eval(line.strip())
                            case 3:
                                goal_position = literal_eval(line.strip())
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

    def _draw_graphs(self):
        """
            Reads log file and creates corresponding graphs.
            Saves graphs if '-log' is active. Shows graphs if '-s' is active.
        """
        # TODO: Implement graph function for non log file graphs by using metrics saved in env/agent

        def _create_figure_fill(self, x, y, title, x_axis, y_axis):
            """
                Creates figure using fill_between
                --------------------------------------------
                Args:
                    x (np.array): x data
                    y (np.array): y data
                    title (String): window title, title of graph
                    x_axis(String): title of x axis
                    y_axis (String): title of y axis
                --------------------------------------------
                Returns:
                    fig, ax: figure and axis
            """
            fig = plt.figure(figsize=[7, 5], num=title)
            ax = plt.subplot(111)
            l = ax.fill_between(x, y)
            # axis
            ax.set_xlabel(x_axis)
            ax.set_ylabel(y_axis)
            xlab = ax.xaxis.get_label()
            ylab = ax.yaxis.get_label()
            xlab.set_style('italic')
            xlab.set_size(10)
            ylab.set_style('italic')
            ylab.set_size(10)
            ax.set_xlim(min(x), max(x))
            ax.set_ylim(min(y), max(y))
            ax.xaxis.set_tick_params(size=0)
            ax.yaxis.set_tick_params(size=0)
            ax.grid('on')
            # title
            ax.set_title(title)
            ax.title.set_weight('bold')
            # style
            l.set_facecolors([[.0, .0, .8, .3]])
            l.set_edgecolors([[.0, .0, .8, .8]])
            l.set_linewidths([2])
            ax.spines['right'].set_color((.8, .8, .8))
            ax.spines['top'].set_color((.8, .8, .8))

            return fig, ax

        def _create_figure(self, x, y, title, x_axis, y_axis):
            """
                Creates figure with simple line as graph
                --------------------------------------------
                Args:
                    x (np.array): x data
                    y (np.array): y data
                    title (String): window title, title of graph
                    x_axis(String): title of x axis
                    y_axis (String): title of y axis
                --------------------------------------------
                Returns:
                    fig, ax: figure and axis
            """
            fig = plt.figure(figsize=[7, 5], num=title)
            ax = plt.subplot(111)
            l = ax.plot(x, y, color=[.0, .0, .8, .8])
            # axis
            ax.set_xlabel(x_axis)
            ax.set_ylabel(y_axis)
            xlab = ax.xaxis.get_label()
            ylab = ax.yaxis.get_label()
            xlab.set_style('italic')
            xlab.set_size(10)
            ylab.set_style('italic')
            ylab.set_size(10)
            ax.set_xlim(min(x), max(x))
            ax.set_ylim(min(y), max(y))
            ax.xaxis.set_tick_params(size=0)
            ax.yaxis.set_tick_params(size=0)
            ax.grid('on')
            # title
            ax.set_title(title)
            ax.title.set_weight('bold')
            # style
            ax.spines['right'].set_color((.8, .8, .8))
            ax.spines['top'].set_color((.8, .8, .8))

            return fig, ax

        action_types = []
        position = []
        time = []
        load = []
        length = []
        action_values = []
        lab = []

        # --- READING DATA ---
        if self.graph:
            # opening and reading file
            with open(args.graph) as file:
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
                                position = np.array(literal_eval(line.strip()))
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
             # path where graphs will be saved
            save_path = self.graph.strip().rsplit('/', 1)[0]

        # --- PREPARING DATA FOR PLOTS ---
        # getting information about action types
        overall_actions = len(action_types)
        unique, counts = np.unique(action_types, return_counts=True)
        action_dict = dict(zip(unique, counts))
        move_number = action_dict.get(
            'NORTH') + action_dict.get('EAST') + action_dict.get('SOUTH') + action_dict.get('WEST')
        turn_number = action_dict.get(
            'TURN LEFT') + action_dict.get('TURN RIGHT')

        # getting time information
        acc_time = np.cumsum(time)
        time_total = acc_time[-1]*1000  # milliseconds
        action_total = len(action_values)
        time_per_action = time_total/action_total  # milliseconds

        # getting action information
        unique_data = [list(x) for x in set(tuple(x) for x in position)]
        visited_total = len(unique_data)
        path_length = length[-1]

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
        for i in range(0, len(position)):
            lab_value[tuple(position[i])] += 1
            lab_time[tuple(position[i])] += time[i]*1000  # milliseconds

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
        ax[1].set_title('Time on tile', fontsize=25, fontweight="bold", y=1.08)

        if self.log:
            fig.figure.savefig(save_path + '/heatmaps.png')

        # Action types table
        df = pd.DataFrame([['TOTAL', overall_actions],
                           ["Total moves", move_number],
                           ["Total turns", turn_number],
                           ['North', action_dict.get('NORTH')],
                           ['East', action_dict.get('EAST')],
                           ['South', action_dict.get('SOUTH')],
                           ['West', action_dict.get('WEST')],
                           ["Turn left", action_dict.get('TURN LEFT')],
                           ["Turn right", action_dict.get('TURN RIGHT')]],
                          columns=['Action type', 'Amount'])
        if self.show:
            print(df)
        if self.log:
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
        df = pd.DataFrame.from_dict({'Minimal cognitive load': load.min(),
                                     "Maximal cognitive load": load.max(),
                                    "Average cognitive load": np.mean(load),
                                     'Cognitive load start': load[0],
                                     'Cognitive load end': load[-1]}, orient="index")
        if self.show:
            print(df)
        if self.log:
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
                                     "Actions in total": action_total,
                                    "Time per action": '{:,.3} ms'.format(time_per_action),
                                     'Path length': path_length,
                                     'Visited ground tiles in total': visited_total,
                                     'Percentage of visited ground tiles': '{:,.2%}'.format(visited_total/number_non_walls)}, orient="index")
        if self.show:
            print(df)
        if self.log:
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
            ])
            dfi.export(df, save_path + '/general_information.png')

        # show plots
        if self.show:
            plt.show()


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
        "-a", "--agent", help="name of the agent that should be used", choices=['wall_follower', 'tremaux', 'directedTremaux'], nargs="+")
    group.add_argument(
        "-p", "--playback", help="file path to .txt file containing log-file that should be replayed")
    group.add_argument(
        "-g", "--graph", help="file path to .txt file containing log-file for which graphs should be generated (no replay)")
    # if -l is used for playback or graph generation only graphs are saved!
    parser.add_argument(
        "-l", "--labyrinth", help=" file path to .txt file containing to be used labyrinth(s)")
    parser.add_argument(
        "-log", "--logging", help="if active pipeline saves experiment in log-file", action="store_true")
    parser.add_argument(
        "-s", "--show", help="if active pipeline shows results after running the experiment", action="store_true")
    # parsing arguments
    args = parser.parse_args()

    # --- PIPELINE START ---
    pipe = pipeline(args)
    pipe.run()
