#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  15 16:59:03 2018
Module containing simple "renderers" for the GridEnvironment code. 
Currently a simpler Matplotlib Renderer is available, which utilices the 
imshow capabilities as well as a somewhat more advanced pygame renderer which
draws the grid and the agent manually.
Colors are defined by the tiles themselves.

@author: jpoeppel
"""

from __future__ import print_function

import matplotlib

matplotlib.use("TKAgg")
import matplotlib.pyplot as plt
import matplotlib.colors as colors

try:
    import pygame

    pygame_available = True
    from pygame import Color, Rect
except ImportError:
    pygame_available = False

import time
import math
import sys


class MatplotlibRenderer(object):
    """
        A simple matplotlib renderer for gridworlds. Needs to have matplotlib
        installed!

        Attributes
        ----------
        fig: matplotlib.Figure
            The figure we are reusing which contains our axes object.
        ax: matplotlib.Axes
            The axes object we are actually drawing onto.
        past_positions: list
            A list of all previously encountered positions, needed to draw
            the past trajectory.
    """

    def __init__(self):
        plt.ion()
        plt.rcParams['toolbar'] = 'None'
        self.fig = self.ax = None
        self.past_positions = []

    def clear_past_trajectory(self):
        """
            Removes any remembered past_positions, which effectively clears
            the past trajectory rendered with "show_trajectory" in the "plot"
            function.
        """
        self.past_positions = []

    def _setup_figure(self):
        self.fig, self.ax = plt.subplots()
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.agent = plt.Circle((0, 0), radius=0.4, color='y')

    def plot(self, grid, agent, show_trajectory=False, past_positions=None):
        """
            Plots the grid and the agent position using matplotlibs 
            pcolormesh.
            
            Parameters
            ---------
            grid: list of lists
                A list of lists containing the Tile object that represent
                the gridworld. 
            agent: Tuple
                A tuple representing the current agent position.
            show_trajectory: bool, optional (Default: False)
                If given, will show the past trajectory, stored in the local
                store. Remember to empty the store when starting a new 
                episode!
            past_positions: list, optional (Default: None)
                A list of past positions which, if given, will override any 
                remembered past positions and are rendered as the past 
                trajectory only if "show_trajectory" is True.
        """

        if self.fig is None:
            self._setup_figure()

        # Convert Tile objects to int array    
        mesh = []
        for row in grid:
            mesh.append([colors.to_rgb(t.color) for t in row])

        self.ax.clear()
        self.ax.imshow(mesh)
        self.agent.center = (agent[1], agent[0])
        self.ax.add_artist(self.agent)

        if show_trajectory:
            # Append current agent positions
            self.past_positions.append(tuple(agent))
            pos_list = self.past_positions
            if past_positions:
                pos_list = past_positions
            xs = [p[1] for p in pos_list]
            ys = [p[0] for p in pos_list]
            self.ax.plot(xs, ys, "r-")

        self.ax.add_artist(self.agent)
        plt.draw()

    def pause(self, duration):
        """
            Stops the executation for the given duration to be able to look
            at the current visualiation.
            
            On some systems/backends, plt.pause might raise a DeprecatedWarning,
            the official solution is to use interaction and time.sleep directly,
            but at least for me, the figure will not be updated in this which
            is why I am using this here.
            
            Parameters
            ----------
            duration: float
                Duration of the pause in seconds.
        """
        plt.pause(duration)

    def close_figure(self):
        """
            Closes the current window.
        """
        if self.fig:
            plt.close(self.fig)
        self.fig = None


class PygameRenderer(object):
    """
        A more complete renderer using pygame. Will only be available if
        pygame is installed.

        Attributes
        ----------
        size: tuple
            A tuple specifying the windowsize of the pygame window.
        screen: pygame.Surface
            The actual surface we are drawing on.
        past_positions: list
            A list of all previously encountered positions, needed to draw
            the past trajectory.
    """

    def __init__(self):
        pygame.init()
        self.size = 620, 480
        self.screen = None

        self.past_positions = []

    def clear_past_trajectory(self):
        """
            Removes any remembered past_positions, which effectively clears
            the past trajectory rendered with "show_trajectory" in the "plot"
            function.
        """
        self.past_positions = []

    def plot(self, grid, agent, facing, show_trajectory=False, past_positions=None):
        """
            Plots the grid and the agent position in the window. Will basically
            overwrite the currently shown image in the window with the new
            grid.
            
            Parameters
            ---------
            grid: list of lists
                A list of lists containing the Tile object that represent
                the gridworld. 
            agent: Tuple
                A tuple representing the current agent position.
            facing: Tuple
                A tuple representing the current direction the agent is facing.
            show_trajectory: bool, optional (Default: False)
                If given, will show the past trajectory, stored in the local
                store. Remember to empty the store when starting a new 
                episode!
            past_positions: list, optional (Default: None)
                A list of past positions which, if given, will override any 
                remembered past positions and are rendered as the past 
                trajectory only if "show_trajectory" is True.
        """
        from .gridEnvironment import NORTH, SOUTH, EAST, WEST
        if self.screen is None:
            self.screen = pygame.display.set_mode(self.size)

        num_rows = len(grid)
        num_cols = len(grid[0])

        tile_width = self.size[0] // num_cols
        tile_height = self.size[1] // num_rows

        self.screen = pygame.display.set_mode((tile_width * num_cols, tile_height * num_rows))

        # Clear old image
        self.screen.fill(Color("white"))

        for i, row in enumerate(grid):
            for j, tile in enumerate(row):
                x = j * tile_width
                y = i * tile_height

                color = Color(tile.color)
                pygame.draw.rect(self.screen, color, Rect(x, y, tile_width, tile_height))

        # Draw agent smiley
        x = int((agent[1] + 0.5) * tile_width)
        y = int((agent[0] + 0.5) * tile_height)
        size = min(tile_height, tile_width) // 2

        # Draw past trajectory if required before drawing the body of the smiley
        # so that the smiley appears on top
        if show_trajectory:
            # Append current agent positions
            self.past_positions.append(agent)

            pos_list = self.past_positions
            if past_positions:
                pos_list = past_positions

            traj_pos = []
            for (p_y, p_x) in pos_list:
                traj_pos.append((int((p_x + 0.5) * tile_width), int((p_y + 0.5) * tile_height)))

            # Draw red line
            if len(traj_pos) > 1:
                pygame.draw.lines(self.screen, Color("red"), False, traj_pos, 2)

        pygame.draw.circle(self.screen, Color("yellow"), (x, y), size)
        if facing == NORTH:
            pygame.draw.circle(self.screen, Color("black"), (x, y - size // 6), size // 6)
        elif facing == SOUTH:
            pygame.draw.circle(self.screen, Color("black"), (x, y + size // 6), size // 6)
        elif facing == EAST:
            pygame.draw.circle(self.screen, Color("black"), (x + size // 6, y), size // 6)
        else:
            pygame.draw.circle(self.screen, Color("black"), (x - size // 6, y), size // 6)

        # Draw eyes
        # pygame.draw.circle(self.screen, Color("black"), (x + size//3,y - size//6), size//6)
        # pygame.draw.circle(self.screen, Color("black"), (x - size//3, y - size//6), size//6)
        # Draw mouth
        # pygame.draw.arc(self.screen, Color("black"), (x - 2*size//3, y - 4*size//5, 4*size//3, 3*size//2), -5*math.pi/6, -math.pi/6, 2)

        pygame.display.update()

    def pause(self, duration):
        if self.screen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
        pygame.time.wait(int(duration * 1000))

    def close_figure(self):
        """
            Closes the current window.
        """
        pygame.display.quit()
        self.screen = None


def show():
    plt.ioff()
    plt.show()
