from AC3 import *
from collections import defaultdict
from SudokuSolver import SudokuSolver


class AC3SudokuSolver(SudokuSolver):
    """
    this class implements backtracking search using arc-consistency
    """
    def solve_sudoku(self, board):
        """
        :type board: puzzle, List[List[str]]
        :rtype: None, we modify the puzzle
        """
        # create the csp problems using SudokuCSP::buildCspProblem
        csp, assigned = self.buildCspProblem(board)
        # run the arc consistency for the initial assignments
        AC3(csp, make_arc_queue(csp, assigned))
        # if we still have uncertain choices for at least one item
        # means we have more than one value in the domain
        uncertain = []
        size = len(board)
        for i in range(size):
            for j in range(size):
                if len(csp.domains[(i, j)]) > 1:
                    uncertain.append((i, j))
        # do the backtracking search with remaining domains and uncertain variables
        self.backtrack(csp, uncertain)
        print('here')
        # when backtrack is complete, make the remaining value the assignment value of the puzzle
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
        # get a uncertain cell
        X = uncertain.pop()
        removals = defaultdict(set)
        # foreach feasible value in domain
        for x in csp.domains[X]:
            domainX = csp.domains[X]
            csp.domains[X] = set([x])
            print(csp.domains)
            # if the assignment was valid
            if AC3(csp, make_arc_queue(csp, [X]), removals):
                retval = self.backtrack(csp, uncertain)
                if retval:
                    return True
            # if the assignment was invalid, restore the previous assignments
            csp.restore_domains(removals)
            csp.domains[X] = domainX
        uncertain.append(X)
        return False
