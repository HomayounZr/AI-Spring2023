from CSP import CSP
import math


class SudokuCSP(CSP):
    def conflicts(self, i1, j1, x, i2, j2, y):
        root = math.floor(math.sqrt(self.size))
        k1 = i1 // root * root + j1 // root
        k2 = i2 // root * root + j2 // root
        return x == y and ( i1 == i2 or j1 == j2 or k1 == k2 )
