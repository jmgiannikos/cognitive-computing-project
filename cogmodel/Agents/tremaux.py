import logging


class tremaux(object):
    """
        Uses the trémaux method to solve labyrinths.
    """

    def __init__(self, gridEnvironment, logging):
        self.env = gridEnvironment  # env on which agent runs
        self.log = logging  # sets if logging is active
        self._action_queue = []  # enqueues/dequeues action to be performed by agent

    def run(self):
        """
            Starts the algorithm on labyrinth given in self.env
        """

        # log header of logging file
        if self.log:
            self.env.start_experiment()

        # --- MAIN ROUTINE ---
        while(self.env.agent_pos != self.env.target):

            # check how many actions are in queue and do all but one
            if(len(self._action_queue) > 1):
                # dequeue action to perform
                action = self._action_queue.pop(0)
                self.env.perform_action(action=action, agent=self)
                
            self._check_walls()    
            break

        # log footer of logging file
        if self.log:
            self.env.finish_experiment()


    def _check_walls(self):
        print(self.env.facing_direction)
        observation = self.env.get_view_cone()
        print(observation)