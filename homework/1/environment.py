'''
Environment class responsible for configuring and running
the MazePitfall problem with BlindBot agent
'''

import os
import re
import sys
import time
import copy
from maze_agent import *

class Environment:
    
    ##################################################################
    # Constants
    ##################################################################
    
    # Simulation constants
    MIN_SCORE   = -100 # if your agent is too dumb, game over!
    PIT_PENALTY = 20
    MOV_PENALTY = 1
    
    # Movement constants + location modifiers
    MOVE_DIRS = {"U": (0, -1), "D": (0, 1), "L": (-1, 0), "R": (1, 0)}
    
    # Maze content constants
    WALL_BLOCK = "X"
    GOAL_BLOCK = "G"
    PIT_BLOCK  = "P"
    SAFE_BLOCK = "."
    PLR_BLOCK  = "@"
    WRN_BLOCK  = "B"
    UNK_BLOCK  = "?"
    
    
    ##################################################################
    # Constructor
    ##################################################################
    
    def __init__ (self, maze, tick_length = 1, verbose = True):
        """
        Initializes the environment from a given maze, specified as an
        array of strings with maze elements
        :maze: The array of strings specifying the challenge
        :tick_length: The duration between agent decisions, in seconds
        :verbose: Whether or not the maze updates will be printed
        """
        self._maze = maze
        self._tick_length = tick_length
        self._verbose = verbose
        self._pits = set()
        self._goals = set()
        
        # Scan for pits and goals in the input maze
        for (row_num, row) in enumerate(maze):
            for (col_num, cell) in enumerate(row):
                if cell == Environment.GOAL_BLOCK:
                    self._goals.add((col_num, row_num))
                if cell == Environment.PIT_BLOCK:
                    self._pits.add((col_num, row_num))
                if cell == Environment.PLR_BLOCK:
                    self._player_loc = self._initial_loc = (col_num, row_num)
        
        breeze_lists = [Environment._get_adjacent(loc) for loc in self._pits]
        self._breezes = {item for sublist in breeze_lists for item in sublist if item not in self._pits and item not in self._goals}

        # Initialize the MazeAgent and ready simulation!
        self._goal_reached = False
        self._ag_maze = self._make_agent_maze()
        self._ag_tile = Environment.SAFE_BLOCK
        self._maze = [list(row) for row in maze] # Easier to change elements in this format
        self._og_maze = copy.deepcopy(self._maze)
        self._og_maze[self._player_loc[1]][self._player_loc[0]] = Environment.SAFE_BLOCK
        for (c, r) in self._breezes:
            self._og_maze[r][c] = Environment.WRN_BLOCK
        self._agent = MazeAgent(self)
    
    
    ##################################################################
    # Methods
    ##################################################################
    
    def get_player_loc (self):
        """
        Returns the player's current location as a maze tuple
        """
        return self._player_loc
    
    def get_agent_maze (self):
        """
        Returns the agent's mental model of the maze, without key
        components revealed that have yet to be explored. Unknown
        spaces are filled with "?"
        """
        return self._ag_maze
    
    def start_mission (self):
        """
        Manages the agent's action loop and the environment's record-keeping
        mechanics
        """
        score = 0
        while (score > Environment.MIN_SCORE):
            time.sleep(self._tick_length)
            
            # Get player's next move in their plan, then execute
            next_act = self._agent.get_next_move()
            self._move_request(next_act)
            
            # Return a perception for the agent to think about and plan next
            perception = {"loc": self._player_loc, "tile": self._ag_tile}
            self._agent.think(perception)
            
            # Assess the post-move penalty and whether or not the game is complete
            penalty = Environment.PIT_PENALTY if self._pit_test(self._player_loc) else Environment.MOV_PENALTY
            score = score - penalty
            if self._verbose:
                print("\nCurrent Loc: " + str(self._player_loc) + " [" + self._ag_tile + "]\nLast Move: " + str(next_act) + "\nScore: " + str(score) + "\n")
            if self._goal_test(self._player_loc):
                break
        
        if self._verbose:
            print("[!] Game Complete! Final Score: " + str(score))
        return score
            
    
    ##################################################################
    # "Private" Helper Methods
    ##################################################################

    @staticmethod
    def _get_adjacent (loc):
        """
        Returns a set of the 4 adjacent cells to the given loc
        """
        (x, y) = loc
        return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    
    def _update_display (self, move):
        for (rowIndex, row) in enumerate(self._maze):
            print(''.join(row) + "\t" + ''.join(self._ag_maze[rowIndex]))
        
    def _wall_test (self, loc):
        (x, y) = loc
        return self._maze[y][x] == Environment.WALL_BLOCK
    
    def _goal_test (self, loc):
        return loc in self._goals
    
    def _breeze_test (self, loc):
        return loc in self._breezes
    
    def _pit_test (self, loc):
        return loc in self._pits
        
    def _make_agent_maze (self):
        """
        Converts the 'true' maze into one with hidden tiles (?) for the agent
        to update as it learns
        """
        sub_regexp = "[" + Environment.PIT_BLOCK + Environment.SAFE_BLOCK + "]"
        return [list(re.sub(sub_regexp, Environment.UNK_BLOCK, r)) for r in self._maze]
    
    def _move_request (self, move):
        old_loc = self._player_loc
        new_loc = old_loc if move == None else tuple(sum(x) for x in zip(self._player_loc, Environment.MOVE_DIRS[move]))
        if self._wall_test(new_loc):
            new_loc = old_loc
        self._update_mazes(self._player_loc, new_loc)
        self._player_loc = new_loc
        if self._verbose:
            self._update_display(move)
    
    def _update_mazes (self, old_loc, new_loc):
        self._maze[old_loc[1]][old_loc[0]] = self._og_maze[old_loc[1]][old_loc[0]]
        self._maze[new_loc[1]][new_loc[0]] = Environment.PLR_BLOCK
        self._ag_maze[old_loc[1]][old_loc[0]] = self._og_maze[old_loc[1]][old_loc[0]]
        self._ag_maze[new_loc[1]][new_loc[0]] = Environment.PLR_BLOCK
        self._ag_tile = self._og_maze[new_loc[1]][new_loc[0]]
    

if __name__ == "__main__":
    """
    Some example mazes with associated difficulties are
    listed below. The score thresholds given are for agents that actually use logic.
    Making a B-line for the goal on these mazes *may* satisfy the threshold listed here,
    but will not in general, more thorough tests.
    """
    mazes = [\
        # Easy difficulty: Score > -20
        ["XXXXXX",
         "X...GX",\
         "X..PPX",\
         "X....X",\
         "X..P.X",\
         "X@...X",\
         "XXXXXX"],

        # Medium difficulty: Score > -30
        ["XXXXXXXXX",
         "X..PGP..X",\
         "X.......X",\
         "X..P.P..X",\
         "X.......X",\
         "X..@....X",\
         "XXXXXXXXX"],
        
        # Hard difficulty: Score > -35
        ["XXXXXXXXX",
         "X..PGP..X",\
         "X.......X",\
         "X.P.P.P.X",\
         "XP.....PX",\
         "X...@...X",\
         "XXXXXXXXX"],
    ]
    
    # Pick your difficulty!
    env = Environment(mazes[1], tick_length = 0) # Call with tick_length = 0 for instant games
    env.start_mission()
