import unittest


import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from cogmodel import Tile
from cogmodel import GridEnvironment
from cogmodel.gridEnvironment import COLOR_MAP, TARGET_COLOR, TARGET_CHAR

class TileTest(unittest.TestCase):

    def test_create_from_wall_string(self):
        tile = Tile("#", 3,2)
        self.assertEqual(tile.pos, (3,2))
        self.assertFalse(tile.passable)
        self.assertEqual(tile.char, "#")
        self.assertEqual(tile.color, COLOR_MAP["#"])

    def test_create_from_ground_string(self):
        tile = Tile("g", 1,4)
        self.assertEqual(tile.pos, (1,4))
        self.assertTrue(tile.passable)
        self.assertEqual(tile.char, "g")
        self.assertEqual(tile.color, COLOR_MAP["g"])

    def test_get_wall(self):
        wall_tile = Tile.get_wall()
        self.assertEqual(wall_tile.passable, False)
        self.assertIsNone(wall_tile.char)
        self.assertEqual(wall_tile.color, "black")

    def test_invisible(self):
        invisible_tile = Tile.invisible()
        self.assertEqual(invisible_tile.pos, (None,None))
        self.assertIsNone(invisible_tile.passable)
        self.assertEqual(invisible_tile.char, "")

    def test_to_dict(self):
        tile = Tile("#", 3,2)
        d = tile.to_dict()
        self.assertEqual(d, {"passable":False, "pos": [3,2], "symbol":"#",
                            "color": COLOR_MAP["#"]})

    def test_unset_target(self):
        tile = Tile("g", 3,2)
        tile2 = tile.clone()
        tile.set_as_target({"color": "red", "symbol":"R"})
        tile.unset_as_target()
        self.assertEqual(tile.to_dict(), tile2.to_dict())

    def test_target_to_dict(self):
        tile = Tile("#", 3,2)
        tile.set_as_target({"color": "red", "symbol":"R"})
        d = tile.to_dict()
        self.assertEqual(d, {"passable":False, "pos": [3,2], "symbol":TARGET_CHAR, 
                            "color":TARGET_COLOR})

    def test_visible_target_to_dict(self):
        tile = Tile("g", 3,2)
        tile.set_as_target({"color": "red", "symbol":"R"})
        tile.target_visible = True
        d = tile.to_dict()
        self.assertEqual(d, {"passable":True, "pos": [3,2], "symbol":"R", 
                            "color":"red"})

    def test_clone_tile(self):
        tile = Tile("g", 3,2)
        tile.set_as_target({"color": "red", "symbol":"R"})
        tile.passable = False

        new_tile = tile.clone()
        # Make sure not to include any functions, because they should be
        # different!
        for attr in [a for a in dir(tile) if not callable(getattr(tile, a))]:
            self.assertEqual(getattr(tile, attr), getattr(new_tile, attr))
    

    def test_clone_tile_make_passable(self):
        tile = Tile("#", 3,2)
        tile.set_as_target({"color": "red", "symbol":"R"})

        new_tile = tile.clone(passable=True)
        # Make sure not to include any functions, because they should be
        # different!
        for attr in [a for a in dir(tile) if not callable(getattr(tile, a))]:
            if attr != "passable" and attr != "__dict__":
                self.assertEqual(getattr(tile, attr), getattr(new_tile, attr))
            else:
                self.assertTrue(getattr(new_tile, attr))
    

class GridEnvironemntTest(unittest.TestCase):

    def setUp(self):
        self.str = "######################\n" + \
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
        self.env = GridEnvironment(self.str)

    def test_init_from_string(self):
        env = GridEnvironment(self.str)
        self.assertEqual(env.size, (15,22))
        for i in range(env.size[0]):
            for j in range(env.size[1]):
                self.assertEqual(env.tiles[(i,j)].pos, (i,j))

        self.assertTrue(env.tiles[1,2].passable)
        self.assertFalse(env.tiles[2,4].passable)
        
    def test_get_action_space(self):
        action_space = self.env.get_action_space()
        for i in [-1,0,1]:
            for j in [-1,0,1]:
                if i*j == 0:
                    self.assertIn((i,j), action_space)

    def test_initialize_agent(self):
        init_pos = (1,1)
        self.env.initialize_agent(init_pos)
        self.assertEqual(self.env.agent_pos, init_pos)

    def test_initialize_agent_twice(self):
        init_pos = (1,1)
        self.env.initialize_agent(init_pos)
        self.assertEqual(self.env.agent_pos, init_pos)
        init_pos2 = (1,2)
        self.env.initialize_agent(init_pos2)
        self.assertNotEqual(self.env.agent_pos, init_pos2)
        self.assertEqual(self.env.agent_pos, init_pos)

    def test_initialize_agent_with_view(self):
        init_pos = (1,5)
        self.env.initialize_agent(init_pos, view_radius=3)
        self.assertEqual(self.env.agent_pos, init_pos)
        self.assertEqual(self.env.view_radius, 3)

    def test_initialize_targets(self):
        t_pos1 = (1,1)
        t_pos2 = (10,9)
        target_pos = [t_pos1, t_pos2]
        targets = {t_pos1: {"color":"Red", "symbol":"R"}, 
                    t_pos2: {"color": "Blue", "symbol":"B"}}
        self.env.initialize_targets(targets)
        for t in target_pos:
            self.assertTrue(self.env.tiles[t].is_target)
            self.assertTrue(t in self.env.targets)


    def test_initialize_targets_twice(self):
        t_pos1 = (1,1)
        t_pos2 = (10,9)
        target_pos1 = [t_pos1, t_pos2]
        targets1 = {t_pos1: {"color":"Red", "symbol":"R"}, 
                    t_pos2: {"color": "Blue", "symbol":"B"}}
        self.env.initialize_targets(targets1)

        t_pos1 = (7,6)
        t_pos2 = (8,4)
        target_pos2 = [t_pos1, t_pos2]
        targets2 = {t_pos1: {"color":"Red", "symbol":"R"}, 
                    t_pos2: {"color": "Blue", "symbol":"B"}}

        self.env.initialize_targets(targets2)
        for t in target_pos1:
            self.assertFalse(self.env.tiles[t].is_target)
            self.assertFalse(t in self.env.targets)

        for t in target_pos2:
            self.assertTrue(self.env.tiles[t].is_target)
            self.assertTrue(t in self.env.targets)

            



    def test_perform_action(self):
        action = (1,0)
        self.env.initialize_agent((1,1))
        new_pos = self.env.perform_action(action)
        self.assertEqual(new_pos, (2,1))

    def test_perform_action_without_set_agent(self):
        action = (1,0)
        with self.assertRaises(AttributeError) as cm:
            self.env.perform_action(action)
        self.assertEqual(str(cm.exception), "No agent was initialized! "\
                            "Cannot perform action {}.".format(action))

    def test_perform_action_with_incorrect_action(self):
        with self.assertRaises(AttributeError) as cm:
            self.env.perform_action((1,1))
        self.assertEqual(str(cm.exception), "(1, 1) is not a valid action " \
                                        "for this environment!")
        with self.assertRaises(AttributeError) as cm:
            self.env.perform_action("Right")
        self.assertEqual(str(cm.exception), "Right is not a valid action " \
                                        "for this environment!")

    def test_perform_action_no_effect(self):
        action = (-1,0)
        self.env.initialize_agent((1,1))
        new_pos = self.env.perform_action(action)
        self.assertEqual(new_pos, (1,1))

    def test_get_observation(self):
        true_list = [[c for c in row] for row in self.str.split("\n")]
        agent_pos = (5,9)
        self.env.initialize_agent(agent_pos)
        obs = self.env.get_observation()
        for i, row in enumerate(obs):
            for j, tile in enumerate(row):
                if true_list[i][j] == "#":
                    self.assertFalse(tile.passable)
                elif true_list[i][j] == "g":
                    self.assertTrue(tile.passable)
                self.assertEqual(tile.pos, (i,j))


    def test_get_observation_radius3(self):
        true_list = [[c for c in row] for row in self.str.split("\n")]
        agent_pos = (5,9)

        visibles = [(4, 6), (4, 7), (4, 8), (4, 9), (4, 10), 
                    (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), 
                    (6, 6), (6, 7), (6, 8), (6, 9), (6, 10)]
        self.env.initialize_agent(agent_pos, view_radius=3)
        obs = self.env.get_observation()
        for i, row in enumerate(obs):
            for j, tile in enumerate(row):
                if (i,j) in visibles:
                    if true_list[i][j] == "#":
                        self.assertFalse(tile.passable)
                    elif true_list[i][j] == "g":
                        self.assertTrue(tile.passable)
                    self.assertEqual(tile.pos, (i,j))
                else:
                    self.assertEqual(tile.pos, (None,None))
                    self.assertIsNone(tile.passable)
                    self.assertEqual(tile.char, "")


    def test_get_observations_with_targets_always(self):
        agent_pos = (10,1)
        target_pos = (11,5)
        self.env.initialize_agent(agent_pos)
        self.env.initialize_targets({target_pos: {"color": "red", "symbol":"R"}}, 
                                    target_radius=None)

        obs = self.env.get_observation()
        self.assertEqual(obs[11][5].color, "red")

        self.env.agent_pos = (11,2)
        obs = self.env.get_observation()
        self.assertEqual(obs[11][5].color, "red")

    def test_get_observations_with_targets_radius(self):
        agent_pos = (10,1)
        target_pos = (11,5)
        self.env.initialize_agent(agent_pos)
        self.env.initialize_targets({target_pos: {"color": "red", "symbol":"R"}}, 
                                    target_radius=3)

        obs = self.env.get_observation()
        self.assertEqual(obs[11][5].color, TARGET_COLOR)

        self.env.agent_pos = (11,2)
        obs = self.env.get_observation()
        self.assertEqual(obs[11][5].color, "red")


    def test_to_json_visible(self):
        true_list = [[c for c in row] for row in self.str.split("\n")]
        agent_pos = (5,9)
        self.env.initialize_agent(agent_pos)
        obs = self.env.get_observation(json=True)
        for i, row in enumerate(obs):
            for j, el in enumerate(row):
                if true_list[i][j] == "#":
                    self.assertFalse(el["passable"])
                elif true_list[i][j] == "g":
                    self.assertTrue(el["passable"])
                self.assertEqual(el["pos"], [i,j])

    def test_to_json_radius3(self):
        true_list = [[c for c in row] for row in self.str.split("\n")]
        agent_pos = (5,9)

        visibles = [(4, 6), (4, 7), (4, 8), (4, 9), (4, 10), 
                    (5, 6), (5, 7), (5, 8), (5, 9), (5, 10), 
                    (6, 6), (6, 7), (6, 8), (6, 9), (6, 10)]
        self.env.initialize_agent(agent_pos, view_radius=3)
        obs = self.env.get_observation(json=True)
        for i, row in enumerate(obs):
            for j, el in enumerate(row):
                if (i,j) in visibles:
                    if true_list[i][j] == "#":
                        self.assertFalse(el["passable"])
                    elif true_list[i][j] == "g":
                        self.assertTrue(el["passable"])
                    self.assertEqual(el["pos"], [i,j])
                else:
                    self.assertEqual(el, Tile.invisible().to_dict())

    def test_is_visible(self):
        agent_pos = (1,1)
        target_pos = (4,1)
        self.env.initialize_agent(agent_pos, view_radius=3)
        is_visible = self.env.is_visible(target_pos)
        self.assertTrue(is_visible)


        target_pos = (1,4)
        self.env.initialize_agent(agent_pos, view_radius=3)
        is_visible = self.env.is_visible(target_pos)
        self.assertTrue(is_visible)

        target_pos = (5,1)
        self.env.initialize_agent(agent_pos, view_radius=3)
        is_visible = self.env.is_visible(target_pos)
        self.assertFalse(is_visible)

    def test_is_visible_custom_radius(self):
        agent_pos = (1,1)
        target_pos = (4,1)
        self.env.initialize_agent(agent_pos, view_radius=6)
        is_visible = self.env.is_visible(target_pos)
        self.assertTrue(is_visible)

        target_pos = (1,4)
        self.env.agent_pos = None
        self.env.initialize_agent(agent_pos, view_radius=1)
        is_visible = self.env.is_visible(target_pos)
        self.assertFalse(is_visible)

        target_pos = (5,1)
        self.env.agent_pos = None
        self.env.initialize_agent(agent_pos, view_radius=4)
        is_visible = self.env.is_visible(target_pos)
        self.assertTrue(is_visible)

    def test_compute_distance_visible(self):
        pos_one = (1,1)
        pos_two = (6,9)
        dist = self.env.compute_distance(pos_one, pos_two)
        self.assertEqual(dist, None)

        start = (8,9)
        end = (5,9)
        dist = self.env.compute_distance(start, end)
        self.assertEqual(dist, 35)

        start = (5,9)
        end = (13,17)
        dist = self.env.compute_distance(start, end)
        self.assertEqual(dist, 50)

    def test_compute_distance_from_wall(self):
        start = (8,2)
        end = (13,17)
        dist = self.env.compute_distance(start, end)
        self.assertEqual(dist, None)

    def test_compute_distance_visible_custom_tiles(self):
        pos_one = (1,1)
        pos_two = (6,9)

        tiles = dict(self.env.tiles)
        # Add shortcut
        tiles[pos_two] = tiles[pos_two].clone(passable=True)
        dist = self.env.compute_distance(pos_one, pos_two, tiles=tiles)
        self.assertEqual(dist, 17)

        start = (8,9)
        end = (5,9)
        dist = self.env.compute_distance(start, end, tiles=tiles)
        self.assertEqual(dist, 3)

        # Close shortcut
        tiles[pos_two] = tiles[pos_two].clone(passable=False)
        dist = self.env.compute_distance(start, end, tiles=tiles)
        self.assertEqual(dist, 35)

    def test_get_distance_partially_visible(self):
        start = (8,9)
        end = (5,9)

        visibles = [(8,8),(8,9),(8,10),(9,8),(9,9),(9,10),
                    (7,8),(7,9),(7,10)]
        dist = self.env.compute_distance_partially_visible(start, end, visibles=visibles)
        self.assertEqual(dist, 3)

        visibles = [(8,8),(8,9),(8,10),(9,8),(9,9),(9,10),
                    (7,8),(7,9),(7,10),(6,8),(6,9),(6,10)]
        dist = self.env.compute_distance_partially_visible(start, end, visibles=visibles)
        self.assertEqual(dist, 7)


    def test_logging(self):
        agent_pos = (10,1)
        target_pos = (11,5)
        self.env.initialize_agent(agent_pos)
        self.env.initialize_targets({target_pos: {"color": "red", "symbol":"R"}}, 
                                    target_radius=3)
        self.env.set_logging("test_log.txt")

        with open("test_log.txt", "r") as f:
            lines = f.readlines()

        self.assertEqual("".join(lines[3:18]).strip(), self.env.env_string)

        os.remove("test_log.txt")
    

    def test_logging_with_actions(self):
        agent_pos = (10,1)
        target_pos = (11,5)
        self.env.initialize_agent(agent_pos)
        self.env.initialize_targets({target_pos: {"color": "red", "symbol":"R"}}, 
                                    target_radius=3)
        self.env.set_logging("test_log.txt")

        self.env.perform_action((0,-1))
        self.env.perform_action((1,0))

        with open("test_log.txt", "r") as f:
            lines = f.readlines()

        self.assertEqual("".join(lines[3:18]).strip(), self.env.env_string)
        self.assertTrue("WEST" in lines[-2])
        self.assertTrue("SOUTH" in lines[-1])

        os.remove("test_log.txt")


if __name__ == "__main__":
    unittest.main()