from cogmodel import GridEnvironment
from cogmodel import renderer
from cogmodel import playback

import time 

if __name__ == "__main__":

    env_str = "######################\n" + \
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

    env = GridEnvironment(env_str)

    env.initialize_agent((1,1))

    if renderer.pygame_available:
        rend = renderer.PygameRenderer()
    else:
        rend = renderer.MatplotlibRenderer()

    #rend = renderer.MatplotlibRenderer()

    rend.plot(env.get_observation(), env.agent_pos)

    # Playback example:
    path = "data/Participant_data/111/condMap3_C3_V1"
    # path = "test_log.txt"
    env, targets, playback_agent, goal_pos = playback.load_experiment(path)

    # Defining view radius
    # env.view_radius = 3

    env.initialize_targets(targets, target_radius = 5)
    rend.plot(env.get_observation(), env.agent_pos, show_trajectory=True)

    manual_replay = True
    def my_callback(pos):
        rend.plot(env.get_observation(), pos, show_trajectory=True)
        rend.pause(0.001) # To allow for event handling and matplotlib updates

    if manual_replay:
        past_pos = [env.agent_pos]
        while True:
            new_pos = playback_agent.perform_action()
            if new_pos is None:
                break
            past_pos.append(new_pos)

            rend.plot(env.get_observation(), env.agent_pos, show_trajectory=True, past_positions=past_pos)
            rend.pause(0.1)

    else: 
        playback_agent.replay(my_callback, speedup=1)

    renderer.show()

