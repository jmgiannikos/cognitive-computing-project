# Cognitive Modeling Environment

This package contains the code framework for the environment used for the
Cognitive Modeling seminar in WS 2018/2019 
(https://ekvv.uni-bielefeld.de/kvv_publ/publ/vd?id=135109752).

It is strongly recommended to use a Python environment (virtualenv, conda env, 
etc)!

## Requirements

The environment does not have any third party requirements. But the simplest
visualization requires matplotlib (will be automatically installed by the
```setup.py```). A more advanced visualization can be used, when ```pygame```
is available on the system, which can be installed using:

```
pip install pygame
```

## Installation

```
python setup.py install
```

## Documentation

You can find API documentation in the ```doc``` folder.
Just run the ```index.html``` and you should find the generated documentation
for the module.

## Data

This repository contains human navigation behavior data data collected in a 
study by Jan Pöppel, originally published as supplementary material to the paper
"Satisficing Models of Bayesian Theory of Mind for Explaining Behavior of
Differnetly Uncertain Agents" by Pöppel and Kopp 
(https://pub.uni-bielefeld.de/record/2917285).

## Usage

The application is simply used with the pipeline via command line arguments. Read this whole section in order to understand what is happening.
You have to use at least python v3.10!

### Available commands
* Showing a list of the currently available options: 
  ```
  python pipeline.py -h
  ```   
  ```
  python pipeline.py --help
  ```
* Running one or multiple agents (on default labyrinth, once): 
  ``` 
  python pipeline.py -a [agent_name1, agent_name2,....]
  ```
  ``` 
  python pipeline.py --agent [agent_name1, agent_name2,....]
  ```
   * There has to be given a least one agent_name out of the following list: ```wall_follower,tremaux,directedTremaux,simple,greedy```
   * The same agent_name can be used multiple times; then they function as separate entity. (However, there is no real use case for this)
* Running one or multiple agents (on given labyrinth(s), once): 
  ``` 
  python pipeline.py -a [agent_name1, agent_name2,....] -l path/to/labyrinths 
  ``` 
  ``` 
  python pipeline.py --agent [agent_name1, agent_name2,....] -l path/to/labyrinths
  ```
  * **WARNING**: The custom labyrinth file *has to* be formatted very strictly (see files in ```cogmodel/Labyrinths```)
* Running on or multiple agents (on default labyrinth, n times): 
  ``` 
  python pipeline.py -a [agent_name1, agent_name2,....] -t n
  ``` 
  ``` 
  python pipeline.py --agent [agent_name1, agent_name2,....] -t n
  ``` 
  where n has to be a natural number >=1 
  * Can also be used with custom labyrinths. 
  * Each agent will run n times over each labyrinth.
* Viewing the playback of an agent: 
  ```
  python pipeline.py -p path/to/logFile
  ```
  ```
  python pipeline.py -playback path/to/logFile
  ```
  * Shows how the agent used to produce the given log-file solves the maze. 
  * **WARNING**: ```pygame``` *has to* be used!

### Generated files when running an agent
Here we will discuss what happens while running two agents (agent1 and agent2) over two labyrinths (lab1 and lab2) two times.All other cases are analogously.

The following folder structure will appear in your ```data``` folder:
<details>
<summary>Click here to open up structure</summary>

```bash
.
├── Agent_data
│   ├── lab1_agent1
│   │   ├── 0
│   │   │   ├── action_types.png
│   │   │   ├── cognitive_load.png
│   │   │   ├── general_information.png
│   │   │   ├── heatmaps.png
│   │   │   └── logging.txt
│   │   ├── 1
│   │   │   ├── action_types.png
│   │   │   ├── cognitive_load.png
│   │   │   ├── general_information.png
│   │   │   ├── heatmaps.png
│   │   │   └── logging.txt
│   │   └── evaluation.csv
│   ├── lab1_agent2
│   │   ├── 0
│   │   │   ├── action_types.png
│   │   │   ├── cognitive_load.png
│   │   │   ├── general_information.png
│   │   │   ├── heatmaps.png
│   │   │   └── logging.txt
│   │   ├── 1
│   │   │   ├── action_types.png
│   │   │   ├── cognitive_load.png
│   │   │   ├── general_information.png
│   │   │   ├── heatmaps.png
│   │   │   └── logging.txt
│   │   └── evaluation.csv
│   ├── lab2_agent1
│   │   ├── 0
│   │   │   ├── action_types.png
│   │   │   ├── cognitive_load.png
│   │   │   ├── general_information.png
│   │   │   ├── heatmaps.png
│   │   │   └── logging.txt
│   │   ├── 1
│   │   │   ├── action_types.png
│   │   │   ├── cognitive_load.png
│   │   │   ├── general_information.png
│   │   │   ├── heatmaps.png
│   │   │   └── logging.txt
│   │   └── evaluation.csv
│   ├── lab2_agent2
│   │   ├── 0
│   │   │   ├── action_types.png
│   │   │   ├── cognitive_load.png
│   │   │   ├── general_information.png
│   │   │   ├── heatmaps.png
│   │   │   └── logging.txt
│   │   ├── 1
│   │   │   ├── action_types.png
│   │   │   ├── cognitive_load.png
│   │   │   ├── general_information.png
│   │   │   ├── heatmaps.png
│   │   │   └── logging.txt
│   │   └── evaluation.csv
│   └── overall_averages.csv
``` 
</details>

As you can see there will be one folder per agent and labyrinth combination. This folder includes two folder for the two runs the agent made; information on each run can be found within these numerated folders. Additional there is a ```evaluation.csv``` file which contains the outcome of both runs in a csv-style and, in addtion, their average outcome. This average outcome, as well as all the average outcomes of the other agent and labyrinth combinations, can also be found in ```overall_averages.csv```. 


**WARNING**: When running the same agent over the same labyrinth another time (using the command line with the same arguments) the same log-file will be used. This leads to it being corrupted and the program crashing. Therefore *always* rename or delete your old files!

### Example usage
The following command produced the outcome in the ```data/Experiment_Data``` folder:
```
python pipeline.py -a wall_follower tremaux directedTremaux simple greedy -l cogmodel/Labyrinths/testLabs -t 10
```
The following command shows the playback of the third run of the tremaux agent on labyrinth testlab2:
```
python pipeline.py -p data/Experiment_data/testlab2_tremaux/2/logging.txt
```
