from collections import defaultdict
from SudokuCSP import SudokuCSP
from math import floor, sqrt


class SudokuSolver(object):
    def __addEdge__(self, i, j, adjList, size):
        """
        create the edged of the constraint graph
        for each point in the same row, column or square,
        create a edge in the graph
        :param i: row
        :param j: column
        :param adj_list: the graph as an adjacency list
        :param size: size of the board
        :return: None
        """
        root = floor(sqrt(size))
        k = i // root * root + j // root
        for num in range(size):
            # add items in the same column
            if num != i:
                adjList[(i, j)].add((num, j))
            # add items in the same row
            if num != j:
                adjList[(i, j)].add((i, num))
            # add items in the same square block
            row = num // root + k // root * root
            col = num % root + k % root * root
            if row != i or col != j:
                adjList[(i, j)].add((row, col))

    def buildCspProblem(self, board):
        """
        build the csp problem with variable, assignments and domains
        :param board: 2d array of the puzzle
        :return: SudokuCSP instance
        """
        adjList = defaultdict(set)
        size = len(board)
        # create the edges in adjacency list for each item
        for i in range(size):
            for j in range(size):
                self.__addEdge__(i, j, adjList, size)
        # Set domains
        variables = []
        assigned = []
        domains = {}
        # find the domains for each item in the puzzle
        for i in range(size):
            for j in range(size):
                if board[i][j] == '.':
                    domains[(i, j)] = set(range(size))
                    variables.append((i, j))
                else:
                    domains[(i, j)] = set([int(board[i][j]) - 1])
                    assigned.append((i, j))
        return SudokuCSP(variables, adjList, domains), assigned

    def solveSudoku(self, board):
        """
        this function will be completed in the child classes instead
        """
        pass
