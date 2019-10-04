'''
BlindBot MazeAgent meant to employ Propositional Logic,
Search, Planning, and Active Learning to navigate the
Maze Pitfall problem
'''

import time
import random
from pathfinder import *
from maze_problem import *
from maze_knowledge_base import *
from queue import Queue

# [!] TODO: import your Part 1 here!

MOVES = ["U", "D", "L", "R"]
agent_kb = MazeKnowledgeBase()

class MazeAgent:
    
    ##################################################################
    # Constructor
    ##################################################################
    
    def __init__ (self, env):
        self.env = env
        self.loc = env.get_player_loc()
        
        # The agent's maze can be manipulated as a tracking mechanic
        # for what it has learned; changes to this maze will be drawn
        # by the environment and is simply for visuals
        self.maze = env.get_agent_maze()
        
        # The agent's plan will be a queue storing the sequence of
        # actions that the environment will execute
        self.plan = Queue()
        # [!] TODO: Initialize any other knowledge-related attributes for
        # agent here, or any other record-keeping attributes you'd like
        print(self._check_wall(self.loc))
        self._find_start_end()
        # want to add to KB that surrounding spaces are safe but need to check if they are walls
        # want to add current position as safe and goal position
        # also want to use pathfinder to plan shortest route to goal 
        # agent_kb.tell()
    
    
    ##################################################################
    # Methods
    ##################################################################
    
    # [!] TODO! Agent currently just runs straight up
    def think(self, perception):
        """
        think is parameterized by the agent's perception of the tile type
        on which it is now standing, and is called during the environment's
        action loop. This method is the chief workhorse of your MazeAgent
        such that it must then generate a plan of action from its current
        knowledge about the environment.
        
        :perception: A dictionary providing the agent's current location
        and current tile type being stood upon, of the format:
          {"loc": (x, y), "tile": tile_type}
        """
        # Agent simply moves randomly at the moment...
        # Do something that thinks about the perception!
        self.plan.put(random.choice(MOVES))
    
    def get_next_move(self):
        """
        Returns the next move in the plan, if there is one, otherwise None
        [!] Do NOT modify this method
        """
        return None if self.plan.empty() else self.plan.get()

    def _check_wall(self, loc):
        x = loc[0]
        y = loc[1]
        if self.maze[y][x] == 'X':
            return True
        else:
            return False

    def _find_start_end(self):
        # returns a list with the start and goal coordinate tuples
        for row in self.maze:
            if '@' in row:
                start = (row.index('@'), self.maze.index(row))
            if 'G' in row:
                goal = (row.index('G'), self.maze.index(row))
        print(start)
        print(goal)
        return [row, goal]