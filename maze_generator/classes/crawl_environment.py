import numpy as np

class crawl_environment(object):

    def __init__(self,dimension=(20,20),maze=None, direction_samples=None,movement_cost=None,population_samples = None):
        
        self.dimension = dimension
        self.starting_point = (1,1)

        if(  maze is None):
            self.maze = np.ones(dimension)
        else:
            self.maze = direction_samples
        

        if(  direction_samples is None):
            self.direction_samples = np.random.random(dimension)
        else:
            self.direction_samples = direction_samples
        
        
        if(  movement_cost is None):
                self.movement_cost= np.full(dimension,0)
        else:
            self.movement_cost = movement_cost
        
        self.movement_cost[:,0] = 1
        self.movement_cost[:,-1] = 1
        self.movement_cost[0,:] = 1
        self.movement_cost[-1,:] = 1

        
        if(  population_samples is None):
            self.population_samples =  np.random.random(dimension)
        else:
            self.population_samples = population_samples
    
    def set_maze_tile(self, position, value):
        self.maze[position[0]][position[1]] = value


    def get_movement_cost(self, position):
        return float((self.movement_cost[position[0]][position[1]]))

    def set_movement_cost(self, position, value):
        self.movement_cost[position[0]][position[1]] = value



    def get_direction_sample(self, position):
        return float((self.direction_samples[position[0]][position[1]]))

    def get_population_sample(self, position):
        return float((self.population_samples[position[0]][position[1]]))
    def set_population_sample(self, position,value):
        self.population_samples[position[0]][position[1]] = value

    def get_maze_tile(self, position):
        return float((self.maze[position[0]][position[1]]))

    def get_paths(self):
        path_fields = []
        for i in range(self.dimension[0]):
            for j in range(self.dimension[1]):
                if(not self.maze[i][j]):
                    path_fields.append((i,j))
        return path_fields

    
    def get_random_starting_point(self):
        self.starting_point = (1,1)
        path_fields = self.get_paths()
        return path_fields[np.random.randint(len(path_fields))]

    def get_random_goal(self):
        path_fields = self.get_paths()
        elligible_fields = list(filter( lambda pos: (pos[0]-self.starting_point[0])**2+(pos[1]-self.starting_point[0])**2 >= (min(self.dimension[0],self.dimension[1])**2 /2 -1), path_fields ))
        return elligible_fields[np.random.randint(len(elligible_fields))]

