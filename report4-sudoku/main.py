import os
from time import time
from sys import stdout
from math import sqrt, floor, ceil
from AC3MRVLCVSudokuSolver import AC3MRVLCVSudokuSolver
from AC3SudokuSolver import AC3SudokuSolver
from copy import deepcopy


class Main:
    def __init__(self, n, c, puzzle):
        self.n = n
        self.c = c
        self.puzzle = puzzle
        self.unsolved_puzzle = deepcopy(puzzle)

    def run(self):
        print("=======>>>>>> INIT PUZZLE <<<<<<=======")
        self.print_board(self.puzzle)

        start = time()
        sol = AC3SudokuSolver()
        sol.solveSudoku(self.puzzle)
        if not self.check_solution(self.puzzle):
            print("CAN NOT SOLVE THE PUZZLE")
            self.print_board(self.puzzle)
            assert False
        print("=======>>>>>> AC3 SOLUTION <<<<<<======")
        stdout.write("\r                    \r")
        print("- %-12s\tRunning time: %f" % ('Solved with AC3', time() - start))
        self.print_board(self.puzzle)

        self.puzzle = deepcopy(self.unsolved_puzzle)
        start = time()
        sol = AC3MRVLCVSudokuSolver()
        sol.solveSudoku(self.puzzle)
        if not self.check_solution(self.puzzle):
            print("CAN NOT SOLVE THE PUZZLE")
            self.print_board(self.puzzle)
            assert False
        print("=======>>>>>> AC3 MRC LCV SOLUTION <<<<<<======")
        stdout.write("\r                    \r")
        print("- %-12s\tRunning time: %f" % ('Solved with AC3 MRV LCV', time() - start))
        self.print_board(self.puzzle)

    def check_solution(self, board):
        nums = set()
        for i in range(self.n):
            nums.add(str(i + 1))
        row_nums = [set() for i in range(self.n)]
        col_nums = [set() for i in range(self.n)]
        square_nums = [set() for i in range(self.n)]
        size_root = int(sqrt(self.n))
        for i in range(self.n):
            for j in range(self.n):
                if board[i][j] not in nums:
                    return False
                k = i // size_root * size_root + j // size_root
                num = int(board[i][j])
                # check if the number has existed in the row, col or square before
                if num in row_nums[i] or num in col_nums[j] or num in square_nums[k]:
                    return False
                row_nums[i].add(num) # add the new number to set of row numbers
                col_nums[j].add(num) # add the new number to set of column numbers
                square_nums[k].add(num) # add the new number to set of numbers in the same sqaure
        return True

    def print_board(self, puzzle):
        root = floor(sqrt(self.n))
        i = 0
        for row in puzzle:
            row_str = ""
            if i % root == 0 and i != 0:
                print('-' * int((root + root - 1) * root + (root - 1) * root))
            for j in range(self.n):
                row_str += str(row[j]) + " "
                if j % root == 2 and j != self.n - 1:
                    row_str += "| "
            print(row_str)
            i += 1


n = int(input())
c = int(input())
puzzle = [['.' for i in range(n)] for j in range(n)]

for number in range(c):
    row, col, value = map(int, input().split())
    puzzle[row][col] = str(value)

Main(n, c, puzzle).run()
