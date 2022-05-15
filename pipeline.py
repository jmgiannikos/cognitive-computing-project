import argparse


class pipeline(object):

    def __init__(self, args):
        self.agent_type = args.agent # string, name of to be used agent
        self.playback = args.playback # file path to .txt file containing playback
        self.labyrinth = args.labyrinth # file path to .txt file containing labyrinths
        self.log = args.logging # bool, toggles logging of results
        self.show = args.show # bool, toggles showing of results
        self.envs = [] # list of all grid environments

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
                    print("Constructing agent")

        elif self.playback:
            # TODO: implement playback here
            print("Playback")
        else:
            print("You either have to use an agent via '-a' or a playback file via '-p'!")
            return -1

    def _construct_envs(self):
        print("Constructing ...")

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
