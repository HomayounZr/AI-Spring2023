import math


class SudokuCSP:
    def __init__(self, variables=[], adjList={}, domains={}, size=9):
        self.variables = variables
        self.adjList = adjList
        self.domains = domains
        self.size = size

    def restore_domains(self, removals):
        """ Undo a supposition and all inferences from it """
        for X in removals:
            self.domains[X] |= removals[X]

    # The following methods are used in min_conflict algorithm
    def nconflicts(self, X1, x, assignment):
        """
        Return the number of conflicts X1 = x has with other variables
        Subclasses may implement this more efficiently
        """
        def conflict(X2):
            return self.conflicts(X1, x, X2, assignment[X2])
        return sum(conflict(X2) for X2 in self.adjList[X1] if X2 in assignment)

    def conflicted_vars(self, current):
        """ Return a list of variables in conflict in current assignment """
        return [var for var in self.variables
                if self.nconflicts(var, current[var], current) > 0]

    def conflicts(self, i1, j1, x, i2, j2, y):
        """
        check to see if two points x and y with coordinates
        (i1, j1) and (i2, j2) have similar values and are
        in the same row or column or square
        """
        root = math.floor(math.sqrt(self.size))
        # find the corresponding squares to each point
        k1 = i1 // root * root + j1 // root
        k2 = i2 // root * root + j2 // root
        return x == y and (i1 == i2 or j1 == j2 or k1 == k2)
