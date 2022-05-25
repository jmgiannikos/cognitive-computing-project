class tremaux(object):
    """
        Uses the trémaux method to solve labyrinths.
    """

    def __init__(self, gridEnvironment):
        self.env = gridEnvironment

    def run(self):
        """
            Starts the algorithm on labyrinth given in self.env
        """
        self.env.start_experiment()
        self.env.finish_experiment()
