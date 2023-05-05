from AC3 import *
from collections import defaultdict
from SudokuSolver import SudokuSolver
from math import floor, sqrt


class AC3SudokuSolver(SudokuSolver):
    """
    this class implements backtracking search using arc-consistency
    """
    def solveSudoku(self, board):
        """
        :type board: puzzle, List[List[str]]
        :rtype: None, we modify the puzzle
        """
        # Build CSP problem
        csp, assigned = self.buildCspProblem(board)
        # Enforce AC3 on initial assignments
        AC3(csp, makeArcQue(csp, assigned))
        # If there's still uncertain choices
        size = len(board)
        uncertain = []
        for i in range(size):
            for j in range(size):
                if len(csp.domains[(i, j)]) > 1:
                    uncertain.append((i, j))
        # Search with backtracking
        self.backtrack(csp, uncertain)
        print('here');
        # Fill answer back to input table
        for i in range(size):
            for j in range(size):
                if board[i][j] == '.':
                    assert len(csp.domains[(i, j)]) == 1
                    board[i][j] = str(csp.domains[(i, j)].pop() + 1)

    def backtrack(self, csp, uncertain):
        """
        just a simple backtracking algorithm
        :param csp:
        :param uncertain:
        :return:
        """
        # if all the variables had only one value in their domain, then RETURN
        if not uncertain:
            return True
        # get an uncertain cell
        X = uncertain.pop()
        removals = defaultdict(set)
        # foreach feasible value in domain
        for x in csp.domains[X]:
            domainX = csp.domains[X]
            csp.domains[X] = set([x])
            # if the assignment was valid
            if AC3(csp, makeArcQue(csp, [X]), removals):
                retval = self.backtrack(csp, uncertain)
                if retval:
                    return True
            # if the assignment was invalid, restore the previous assignments
            csp.restore_domains(removals)
            csp.domains[X] = domainX
        uncertain.append(X)
        return False
