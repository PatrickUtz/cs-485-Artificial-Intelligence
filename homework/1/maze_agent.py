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

class MazeAgent:
    
    ##################################################################
    # Constructor
    ##################################################################
    
    def __init__ (self, env):
        # The agent's maze can be manipulated as a tracking mechanic
        # for what it has learned; changes to this maze will be drawn
        # by the environment and is simply for visuals
        self.maze = env.get_agent_maze()
        
        # The agent's plan will be a queue storing the sequence of
        # actions that the environment will execute
        self.plan = Queue()

        self.agent_kb = MazeKnowledgeBase()
        self.env = env
        self.loc = env.get_player_loc()
        start_end_list = self._find_start_end()
        self.goal = start_end_list[1]
        self.agent_kb.tell(MazeClause([(("P", self.goal), False)]))
        self.agent_kb.tell(MazeClause([(("P", self.loc), False)]))
        no_wall_list = self._no_walls_list()
        for spot in no_wall_list:
            self.agent_kb.tell(MazeClause([(("P", spot), False)]))

        # let's create a path!
        mp = MazeProblem(self.maze)
        path = pathfind(mp, self.loc, self.goal)
        for action in path[1]:
            self.plan.put(action)
    
    
    ##################################################################
    # Methods
    ##################################################################
    
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
        
        # update current location
        self.loc = perception["loc"]
        
        # analyze/add current tile agent is on
        if perception["tile"] == "B":
            no_walls_breeze_list = self._no_walls_list()
            pit_list = []
            for pit_spot in no_walls_breeze_list:
                pit_list.append((("P", pit_spot), True))
            self.agent_kb.tell(MazeClause(pit_list))

        if perception["tile"] == ".":
            no_walls_breeze_list = self._no_walls_list()
            for pit_spot in no_walls_breeze_list:
                self.agent_kb.tell(MazeClause([(("P", pit_spot), False)]))

        if perception["tile"] == "P":
            self.agent_kb.tell(MazeClause([(("P", self.loc), True)]))
        
        # analyze/add adjacent tiles and update path if needed
        adj_spots = self._no_walls_list()
        updated = False
        for spot in adj_spots:
            test_x = spot[0]
            test_y = spot[1]
            isPit = self.agent_kb.ask(MazeClause([(("P", (test_x, test_y)), True)]))
            isNotPit = self.agent_kb.ask(MazeClause([(("P", (test_x, test_y)), False)]))
            if isNotPit and (self.maze[test_y][test_x] != "." and self.maze[test_y][test_x] != "B"):
                updated = True
                self.maze[test_y][test_x] = "S"
            if isPit and self.maze[test_y][test_x] != "P":
                updated = True
                self.maze[test_y][test_x] = "P"
            if not isPit and not isNotPit and (self.maze[test_y][test_x] == "U" or self.maze[test_y][test_x] == "?"):
                updated = True
                self.maze[test_y][test_x] = "U"
            if updated:
                self.plan.queue.clear()
                mp = MazeProblem(self.maze)
                path = pathfind(mp, self.loc, self.goal)
                for action in path[1]:
                    self.plan.put(action)
        return

    def get_next_move(self):
        """
        Returns the next move in the plan, if there is one, otherwise None
        [!] Do NOT modify this method
        """
        return None if self.plan.empty() else self.plan.get()

    def _is_wall(self, loc):
        x = loc[0]
        y = loc[1]
        if self.maze[y][x] == 'X':
            return True
        else:
            return False

    def _find_start_end(self):
        # returns a list of tuples that are the start and goal coordinates
        for row in self.maze:
            if '@' in row:
                start = (row.index('@'), self.maze.index(row))
            if 'G' in row:
                goal = (row.index('G'), self.maze.index(row))
        return [start, goal]

    def _no_walls_list(self):
        # returns a list of tuples of adjacent tiles that are NOT walls
        (x, y) = self.loc
        adj_spots = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        no_wall_list = []
        for spot in adj_spots:
            if not self._is_wall(spot):
                no_wall_list.append(spot)
        return no_wall_list