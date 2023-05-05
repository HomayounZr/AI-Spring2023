from collections import defaultdict
from SudokuCSP import SudokuCSP
import math

class SudokuSolver(object):
    def __addEdge__(self, i, j, adjList, size):
        root = math.floor(math.sqrt(size))
        k = i // root * root + j // root
        for num in range(size):
            if num != i:
                adjList[(i, j)].add((num, j))
            if num != j:
                adjList[(i, j)].add((i, num))
            row = num//root + k//root * root
            col = num%root + k%root * root
            if row != i or col != j:
                adjList[(i, j)].add((row, col))

    def buildCspProblem(self, board):
        adjList = defaultdict(set)
        # Build graph (contraints)
        size = len(board)
        for i in range(size):
            for j in range(size):
                self.__addEdge__(i, j, adjList, size)
        # Set domains
        variables = []
        assigned = []
        domains = {}
        for i in range(size):
            for j in range(size):
                if board[i][j] == '.':
                    domains[(i, j)] = self.get_domain(board, adjList[(i, j)])
                    variables.append((i, j))
                else:
                    # domains[(i, j)] = set([int(board[i][j]) - 1])
                    domains[(i, j)] = set([int(board[i][j]) - 1])
                    assigned.append((i, j))
        return SudokuCSP(variables, adjList, domains), assigned

    def solveSudoku(self, board):
        """
        :type board: List[List[str]]
        :rtype: void Do not return anything, modify board in-place instead.
        """
        pass

    def get_domain(self, board, neighbours):
        default_domain = set(range(9))
        for (row, col) in neighbours:
            value = board[row][col]
            if value != '.' and (int(value) - 1) in default_domain:
                default_domain.remove(int(value) - 1)
        return default_domain