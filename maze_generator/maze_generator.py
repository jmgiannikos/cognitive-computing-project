import numpy as np
import sys
from classes.crawler import crawler
from classes.crawl_environment import crawl_environment



dimension =  tuple(map(int, sys.argv[1].split(',')))

testarray = np.array(
    [
        [1,1,1,1,1,1,1],
        [1,0,0,0,0,0,1],
        [1,1,1,1,1,0,1],
        [1,0,0,0,0,0,1],
        [1,0,1,1,1,1,1],
        [1,0,0,0,0,0,1],
        [1,1,1,1,1,1,1],

    ]
)


environment = crawl_environment(dimension,direction_samples=np.full(dimension,0))


crawlers = [crawler(environment,(1,1),population_chance=(0.5,0.8))]

steps = 0


while(steps<400):

    for cr in crawlers:

        new_crawlers=cr.move()
        for new_crs in new_crawlers:
            crawlers.append(new_crs)
    

 
        

    steps+=1

print(environment.maze)

print(environment.movement_cost)   

#write to file
with open('maze.txt', 'w') as file:
    for row in environment.maze:
        for field in row:
            if(field):
                
                file.write("#")
            else:
                file.write("g")
        file.write("\n")

file.close()
    