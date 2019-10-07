'''
maze_knowledge_base.py
Authors:
Jeremy Goldberg
Kevin McInerney
Patrick Utz
Specifies a simple, Conjunctive Normal Form Propositional
Logic Knowledge Base for use in Grid Maze pathfinding problems
with side-information.
'''
from maze_clause import MazeClause
import unittest
import itertools

class MazeKnowledgeBase:
    
    def __init__ (self):
        self.clauses = set()
    
    def tell (self, clause):
        """
        Adds the given clause to the CNF MazeKnowledgeBase
        Note: we expect that no clause added this way will ever
        make the KB inconsistent (you need not check for this)
        """
        self.clauses.add(clause)
        return
        
    def ask (self, query):
        """
        Given a MazeClause query, returns True if the KB entails
        the query, False otherwise
        """
        # TODO: Implement resolution inference here!
        # This is currently implemented incorrectly; see
        # spec for details!
        
        # create copy of clauses
        temp_clauses = self.clauses.copy()

        # negate query and add to set of cluases
        for key in query.props:
            query.props[key] = not query.props[key]
        temp_clauses.add(query)
        new_clauses = set()

        while True:
            # iterate through each pair
            for pair in itertools.combinations(temp_clauses, 2):
                resolved_clause = MazeClause.resolve(pair[0], pair[1])
                if (len(resolved_clause) == 1):
                    resolved_clause_check = resolved_clause.pop()
                    if resolved_clause_check.is_empty():
                        return True
                    resolved_clause.add(resolved_clause_check)
                    new_clauses.update(resolved_clause)
            if new_clauses.issubset(temp_clauses):
                return False
            temp_clauses.update(new_clauses)

class MazeKnowledgeBaseTests(unittest.TestCase):
    def test_mazekb1(self):
        kb = MazeKnowledgeBase()
        kb.tell(MazeClause([(("X", (1, 1)), True)]))
        self.assertTrue(kb.ask(MazeClause([(("X", (1, 1)), True)])))
        
    def test_mazekb2(self):
        kb = MazeKnowledgeBase()
        kb.tell(MazeClause([(("X", (1, 1)), False)]))
        kb.tell(MazeClause([(("X", (1, 1)), True), (("Y", (1, 1)), True)]))
        self.assertTrue(kb.ask(MazeClause([(("Y", (1, 1)), True)])))
        
    def test_mazekb3(self):
        kb = MazeKnowledgeBase()
        kb.tell(MazeClause([(("X", (1, 1)), False), (("Y", (1, 1)), True)]))
        kb.tell(MazeClause([(("Y", (1, 1)), False), (("Z", (1, 1)), True)]))
        kb.tell(MazeClause([(("W", (1, 1)), True), (("Z", (1, 1)), False)]))
        kb.tell(MazeClause([(("X", (1, 1)), True)]))
        self.assertTrue(kb.ask(MazeClause([(("W", (1, 1)), True)])))
        self.assertFalse(kb.ask(MazeClause([(("Y", (1, 1)), False)])))


if __name__ == "__main__":
    unittest.main()