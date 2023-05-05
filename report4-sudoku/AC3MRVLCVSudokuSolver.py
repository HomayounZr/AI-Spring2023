from AC3SudokuSolver import AC3SudokuSolver
from AC3 import *
from random import choice

# AC3 filtering with Minimum Remaining Values and Least Constraining Value
# ordering
class AC3MRVLCVSudokuSolver(AC3SudokuSolver):
    def count_conflict(self, csp, Xi, x):
        cnt = 0
        for X in csp.adj_list[Xi]:
            if x in csp.domains[X]:
                cnt += 1
        return cnt

    def popMin(self, array, key):
        minimum, idx = float("inf"), 0
        for i in range(len(array)):
            if key(array[i]) < minimum:
                idx = i
                minimum = key(array[i])
        array[idx], array[-1] = array[-1], array[idx]
        return array.pop()

    def solve_sudoku(self, board):
        """
        :type board: List[List[str]]
        :rtype: void Do not return anything, modify board in-place instead.
        """
        # create the csp problems using SudokuCSP::buildCspProblem
        csp, assigned = self.buildCspProblem(board)
        # run the arc consistency for the initial assignments
        if not AC3(csp, make_arc_queue(csp, assigned)):
            return False
        # if we still have uncertain choices for at least one item
        # means we have more than one value in the domain
        uncertain = []
        size = len(board)
        for i in range(size):
            for j in range(size):
                if len(csp.domains[(i, j)]) > 1:
                    uncertain.append((i, j))
        # do the backtracking search with remaining domains and uncertain variables
        if not self.backtrack(csp, uncertain):
            return False
        # when backtrack is complete, make the remaining value the assignment value of the puzzle
        for i in range(size):
            for j in range(size):
                if board[i][j] == '.':
                    assert len(csp.domains[(i, j)]) == 1
                    board[i][j] = str( csp.domains[(i, j)].pop() + 1 )
        return True

    def backtrack(self, csp, uncertain):
        # if all the variables had only one value in their domain, then RETURN
        if not uncertain:
            return True
        # get the cell with its minimum remaining values in its domain (MRV)
        X = self.popMin(uncertain, key=lambda X: len(csp.domains[X]))
        removals = defaultdict(set)

        domainlist = list(csp.domains[X])
        # now we sort the values in the variable domain, based on least conflict with others
        domainlist.sort(key=lambda x: self.count_conflict(csp, X, x))
        for x in domainlist:
            domainX = csp.domains[X]
            csp.domains[X] = set([x])
            # if the assignment was consistent, then return
            if AC3(csp, make_arc_queue(csp, [X]), removals):
                retval = self.backtrack(csp, uncertain)
                if retval:
                    return True
            # if assignment was inconsistent, return the previous state
            csp.restore_domains(removals)
            csp.domains[X] = domainX
        uncertain.append(X)
        return False
