import argparse
from ast import literal_eval
from cogmodel import GridEnvironment
from cogmodel import renderer
from cogmodel import playback


class pipeline(object):

    def __init__(self, args):
        self.agent_type = args.agent  # string, name of to be used agent
        self.playback = args.playback  # file path to .txt file containing playback
        self.labyrinth = args.labyrinth  # file path to .txt file containing labyrinths
        self.log = args.logging  # bool, toggles logging of results
        self.show = args.show  # bool, toggles showing of results
        self.envs = []  # list of all grid environments

    def run(self):
        """
            Runs and controls pipeline
        """

        if self.agent_type:
            # constructing grid environment(s)
            self._construct_envs()
            # TODO add other available agents
            match self.agent_type:
                case "wall_follower":
                    # TODO make agent once available
                    for env in self.envs:
                        print("Constructing agent")

        elif self.playback:
            self._playback()
        else:
            print("You either have to use an agent via '-a' or a playback file via '-p'!")
            return -1

    def _construct_envs(self):
        """
            Reads labyrinth(s) from .txt file and creates fitting environments
        """

        def _add_env(self):
            """
                Initializes gridEnvs and adds them to envs list
            """
            env = GridEnvironment(env_string=env_string)
            # TODO add agent_facing once possible, add view_radius once discussed
            env.initialize_agent(initial_agent_pos=start_postion)
            # TODO see if this changed
            env.initialize_targets(
                targets={goal_position: {"symbol": "T", "color": "green"}})
            if self.log:
                log_path = "data/Agent_data/" + \
                    str(name) + "_" + str(self.agent_type)
                env.set_logging(path=log_path)
            self.envs.append(env)

        # information used to generate environment
        env_string = ""
        start_postion = ()
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
                                start_postion = literal_eval(line.strip())
                            case 3:
                                goal_position = literal_eval(line.strip())
                            case 4:
                                facing = line.strip()
                            case 5:
                                name = line.strip()
                                _add_env(self)
                                read_point = 0
                                env_string = ""
                                start_postion = ()
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
            start_postion = (13, 17)
            goal_position = (5, 9)
            facing = "NORTH"
            name = "Default Labyrinth"
            _add_env(self)

    def _playback(self):
        """
            Play backs logging file given by user.
        """

        # The following code is taken from example.py; will need to be adjusted once Issue#2 is resolved
        if renderer.pygame_available:
            rend = renderer.PygameRenderer()
        else:
            rend = renderer.MatplotlibRenderer()

        env, targets, playback_agent, goal_pos = playback.load_experiment(
            self.playback)
        env.initialize_targets(targets, target_radius=5)
        rend.plot(env.get_observation(), env.agent_pos, show_trajectory=True)

        def my_callback(pos):
            rend.plot(env.get_observation(), pos, show_trajectory=True)
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
        "-a", "--agent", help="name of the agent that should be used", choices=['wall_follower'])
    group.add_argument(
        "-p", "--playback", help="file path to .txt file containing log-file that should be replayed")
    # -l can still  be used if pipeline is used for playback, however, it does not do anything
    parser.add_argument(
        "-l", "--labyrinth", help=" file path to .txt file containing to be used labyrinth(s)")
    parser.add_argument(
        "-log", "--logging", help="if active pipeline saves experiment in log-file", action="store_true")
    # TODO: maybe do other way around
    parser.add_argument(
        "-s", "--show", help="if active pipeline shows results after running the experiment", action="store_true")
    # parsing arguments
    args = parser.parse_args()

    # --- PIPELINE START ---
    pipe = pipeline(args)
    pipe.run()
