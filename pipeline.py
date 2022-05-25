import argparse
from json import load
from operator import length_hint
from turtle import position
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
from cogmodel.gridEnvironment import GridEnvironment
from cogmodel import renderer
from cogmodel import playback
from cogmodel.Agents.tremaux import tremaux

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
                            agent = tremaux(env)
                            agent.run()
                            # TODO: add graphs if wanted here

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
                                facing = line.strip()
                            case 5:
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
            env_string = "######################\n" + \
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
            start_position = (13, 17)
            goal_position = (5, 9)
            facing = "NORTH"
            name = "Default Labyrinth"
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
                            facing = line.strip()
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

        env = GridEnvironment(target=goal_position, initial_agent_pos=start_position,
                              view_radius=VIEW_RADIUS, env_string=env_string, facing=facing)
        playback_agent = playback.PlaybackAgent(
            agent_id=agent_type, action_rows=action_rows, start_pos=start_position, environment=env)

        rend.plot(grid=env.get_observation(), agent=env.agent_pos,
                  facing=env.facing_direction, show_trajectory=True)

        def my_callback(pos):
            rend.plot(grid=env.get_observation(), agent=pos,
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

        def _read_file(self):
            """
                Processes metric information in file from path given by user
                ------------------------------------------------------------
                Returns:
                    position, time, load, length, action: np.array that contain corresponding information
            """
            # opening and reading file
            with open(args.graph) as file:
                read_point = 0
                while(line := file.readline()):
                    if line in ["Position:\n", "Time:\n", "Load:\n", "Length:\n", "Action:\n"]:
                        read_point += 1
                    else:
                        match read_point:
                            case 0:
                                continue
                            case 1:
                                position = np.array(literal_eval(line.strip()))
                            case 2:
                                time = np.array(literal_eval(line.strip()))
                            case 3:
                                load = np.array(literal_eval(line.strip()))
                            case 4:
                                length = np.array(literal_eval(line.strip()))
                            case 5:
                                action = np.array(literal_eval(line.strip()))
                            case _:
                                print(
                                    "Something went wrong while trying to read the log file.")
                                return -1

            return position, time, load, length, action

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

        position = np.array([])
        time = np.array([])
        load = np.array([])
        length = np.array([])
        action = np.array([])

        if self.graph:
            position, time, load, length, action = _read_file(self)
            save_path = self.graph.strip().rsplit('/', 1)[0]
            print(save_path)

        # --- PLOTS ---

        # TODO find better way to save figures

        #  load over time
        fig1, ax1 = _create_figure_fill(self, time, load, "Cognitive load over time",
                                        "Time in [seconds]", "Cognitive load in [number of saved numbers]")
        if self.log:
            plt.savefig(save_path+"/load_time")

        # load over state number
        fig2, ax2 = _create_figure_fill(self, np.arange(len(load)), load, "Cognitive load over number of visited states",
                                        "State in [number]", "Cognitive load in [number of saved numbers]")
        if self.log:
            plt.savefig(save_path+"/load_state")
        # path length over time
        fig3, ax3 = _create_figure(
            self, time, length, "Path length over time", "Time in [seconds]", "Path length in [unit]")
        if self.log:
            plt.savefig(save_path+"/length_time")

        # path length over state number
        fig4, ax4 = _create_figure(
            self,  np.arange(len(length)), length, "Path length over number of visited states", "State in [number]", "Path length in [unit]")
        if self.log:
            plt.savefig(save_path+"/length_state")

        # action number of time
        fig5, ax5 = _create_figure(
            self, time, action, "Number of actions over time", "Time in [seconds]", "Action in [number]")
        if self.log:
            plt.savefig(save_path+"/action_time")

        # action number over state number
        fig6, ax6 = _create_figure(
            self, np.arange(len(action)), action, "Number of actions over number of visited states", "State in [number]", "Action in [number]")
        if self.log:
            plt.savefig(save_path+"/action_state")

        # state number over time
        fig7, ax7 = _create_figure(
            self, time, np.arange(len(time)), "Number of visited states over time", "Time in [seconds]", "State in [number]")
        if self.log:
            plt.savefig(save_path+"/state_time")

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
        "-a", "--agent", help="name of the agent that should be used", choices=['wall_follower', 'tremaux'], nargs="+")
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
