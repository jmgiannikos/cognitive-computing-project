from tracemalloc import start
import numpy as np
import sys

from classes.crawler import crawler
from classes.crawl_environment import crawl_environment
from PIL import Image


#Are is there a Dimension?
if(len(sys.argv)<2):
    print("Usage: <x-Dimension>,<y-Dimension>  (optional)<Maze Textfile Location> (optional)<Maze Image Location> (optional)<Image Input>")
    exit()
dimension =  tuple(map(int, sys.argv[1].split(',')))


#Is there a save path for the maze textfile
if(len(sys.argv)>2):
    save_txt_path = sys.argv[2]
else:
    save_txt_path =None

#Is there a sav file for the maze image
if(len(sys.argv)>3):
    save_image_path = sys.argv[3]
else:
    save_image_path =None


#is there an input image, set environment accordingly
if(len(sys.argv)>4):
    image_path = sys.argv[4]
    
    
    image = Image.open(image_path)
    
    data_from_image = np.divide(np.asarray(image),255)
    movement_costs_from_image = np.divide(data_from_image[:,:,0], 80)
    dimension = movement_costs_from_image.shape
    movement_costs_from_image = np.full(dimension,0)
    direction_samples_from_image = data_from_image[:,:,1]
    population_samples_from_image= data_from_image[:,:,2]
    

    print(movement_costs_from_image.shape)
    
    
    environment = crawl_environment(dimension, movement_cost=movement_costs_from_image, direction_samples=direction_samples_from_image, population_samples=population_samples_from_image)

else:
    environment = crawl_environment(dimension)




# Generating the Maze
crawlers = [crawler(environment,population_chance=(0.5,0.95))]
steps = 0


while(steps<5000 and len(crawlers)>0):
    next_crawlers = []
    for cr in crawlers:

        new_crawlers=cr.move()
        for new_crs in new_crawlers:
            crawlers.append(new_crs)
        if(cr.life>0):
            next_crawlers.append(cr)

    crawlers = next_crawlers.copy()

        

    steps+=1


#Get a random starting point
starting_point = environment.get_random_starting_point()
goal = environment.get_random_goal()


#write to file
if(not (save_txt_path is None)):
    with open(save_txt_path, 'w') as file:
        for row in environment.maze:
            for field in row:
                if(field):
                
                    file.write("#")
                else:
                    file.write("g")
            file.write("\n")
        file.write("Starting Point: ")
        file.write(str(starting_point))
        file.write("\n")
        file.write("Goal: ")
        file.write(str(goal))
        file.write("\n")
        file.close()   



if(not (save_image_path is None)):
    bw_arr = np.array(np.reshape((255-environment.maze*255).astype(np.uint8), dimension))
    im_arr = np.stack((bw_arr,bw_arr,bw_arr),axis=-1)
    im_arr[goal[0],goal[1]] = np.array([255,0,0])
    im_arr[starting_point[0],starting_point[1]] = np.array([0,0,255])
    im = Image.fromarray(im_arr)
    im.save(save_image_path)