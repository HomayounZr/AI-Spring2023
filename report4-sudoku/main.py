from time import time
from sys import stdout
from AC3MRVLCVSudokuSolver import AC3MRVLCVSudokuSolver


class Main:
    def run(self):
        print("Homayoun Zarei - 9822019")
        print("AI Report 4 - Sudoku solver using csp")

        with open("general_test.txt", "r") as fd:
            cases = list(map(eval, fd.read().splitlines()))

        start = time()
        sol = AC3MRVLCVSudokuSolver()
        for i, case in enumerate(cases):
            stdout.write( "\rProgress: " + "%d/%d" % (i + 1, len(cases)) )
            stdout.flush()
            sol.solveSudoku(case)
            if not self.checkSolution(case):
                print("Case %d failed\n" % i + self.printBoard(case))
                assert False
        stdout.write("\r                    \r")
        print("- %-12s\tRunning time: %f" % ("AC3 MRV LCV", time() - start))

    def checkSolution(self, board):
        nums = set("123456789")
        heng = [set() for i in range(9)]
        zong = [set() for i in range(9)]
        gezi = [set() for i in range(9)]
        for i in range(9):
            for j in range(9):
                if board[i][j] not in nums:
                    return False
                k = i // 3 * 3 + j // 3
                num = int(board[i][j]) - 1
                if num in heng[i] or num in zong[j] or num in gezi[k]:
                    return False
                heng[i].add(num)
                zong[j].add(num)
                gezi[k].add(num)
        return True

    def printBoard(self, board):
        return "\n".join(map(" ".join, board))


Main().run()
