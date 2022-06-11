import numpy as np
from classes.crawl_environment import crawl_environment

class crawler(object):
    """
        A simple crawler that can move according to a number. Used for Maze generation

        Attributes
        ----------
        position: int
            The position of the crawler

    """
    
    def __init__(self,environment,position=None,life=1, population_chance=(0.5,0.8),uniform=True):
        self.environment = environment
        if(position is None):
            self.position= tuple((round(environment.dimension[0]/2),round(environment.dimension[1]/2)))
        else:
            self.position = position
        
        self.life = life
        self.all_directions = np.array([(-1,0),(0,1),(1,0),(0,-1)])
        self.direction_probabilities = np.array([0.125,0.375,0.625,0.875])
        self.population_chance = population_chance

        self.old_position = position
        self.environment.set_maze_tile(self.position,0)
        self.environment.set_movement_cost(self.position,1)
        self.refractory=2
        self.uniform = uniform

        
    




    def update_possible_directions(self):
        for i in range(4):
            if ((self.environment.get_movement_cost((self.position+self.all_directions[i])))<self.life):
                self.direction_probabilities[i] = 0.25*i+0.125
            else:
                self.direction_probabilities[i] = 2


    def update_possible_directions_uniform(self):
        neighbors = 4-self.get_neighboring_paths()
        j = 0

        for i in range(4):
            if ((self.environment.get_movement_cost((self.position+self.all_directions[i])))<self.life):
                self.direction_probabilities[i] = (1/neighbors)*j+0.125
            else:
                self.direction_probabilities[i] = 2


    def choose_direction(self):
        if (self.uniform):
            self.update_possible_directions_uniform()
        else:
            self.update_possible_directions()
        direction_sample = self.environment.get_direction_sample(self.position)

        choosing_direction = [abs(dir_prob-direction_sample) for dir_prob in self.direction_probabilities]

        
        direction_index = choosing_direction.index(min(choosing_direction))

        return direction_index
    
    def move(self):
        direction_index = self.choose_direction()
        new_crawlers =[]

        self.old_position=tuple(self.position)
        self.position += self.all_directions[direction_index]
        self.lose_life(self.environment.get_movement_cost(self.position))
        self.environment.set_movement_cost(self.position,1)
        
        if(self.refractory>0):
            self.refractory -=1

        #print(self.get_neighboring_paths())
        if(self.get_neighboring_paths()>=2):
            self.environment.set_movement_cost(self.position,1)
            self.position= tuple(self.old_position)

            self.refractory +=1
        elif(self.life>0):
            
        
            new_crawlers=self.populate()
            #Settting 'borders' at the path
            for dir in self.all_directions:
                self.environment.set_movement_cost((self.old_position+dir),1)


            self.environment.set_maze_tile(self.position,0)
            self.environment.set_movement_cost(self.old_position,1)
        else:
            self.position= tuple(self.old_position)
            self.refractory +=1

            
            #print("Not Moved")
            #print(self.position)

        return new_crawlers



    def lose_life(self,amount):
        self.life -=amount


    def populate(self):
        new_crawler_list = []
        if(self.refractory <=0):
            population_sample = self.environment.get_population_sample(self.position)
            if(population_sample>self.population_chance[1]):
                new_crawler = crawler(self.environment,self.old_position,population_chance=self.population_chance)
                new_crawler.move()
                new_crawler_list.append(new_crawler)
                #print("Breed 1")
            if(population_sample>self.population_chance[0]): 
                new_crawler = crawler(self.environment,self.old_position,population_chance=self.population_chance)
                new_crawler.move()
                new_crawler_list.append(new_crawler)
                #print("Breed 2")

        return new_crawler_list

    def get_neighboring_paths(self):
        sum=0.0
        for dir in self.all_directions:
            sum+= 1.0-self.environment.get_maze_tile(self.position+dir)
        return sum

    def copy(self):
        return crawler( self.environment, tuple(self.position), int(self.life), tuple(self.old_position),tuple(self.population_chance))

