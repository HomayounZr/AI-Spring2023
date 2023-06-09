from collections import defaultdict



def AC3(csp, queue=None, removals=defaultdict(set)):
    """
    this is the main arc-consistency algorithm
    :param csp: SudokuCSP problem
    :param queue: queue of all the arcs
    :param removals: removed domains
    :return:
    """
    # Return False if there is no consistent assignment
    if queue is None:
        queue = [(Xt, X) for Xt in csp.adjList for X in csp.adjList[Xt]]
    # Queue of arcs of our concern
    while queue:
        # Xt --> Xh Delete from domain of Xt
        (Xt, Xh) = queue.pop()
        if remove_inconsistent_values(csp, Xt, Xh, removals):
            if not csp.domains[Xt]:
                return False
            # NOTE: Next two lines only for binary "!=" constraint
            elif len(csp.domains[Xt]) > 1:
                continue
            for X in csp.adjList[Xt]:
                if X != Xt:
                    queue.append((X, Xt))
    return True

def remove_inconsistent_values(csp, Xt, Xh, removals):
    """
    this function checks domain values of tail, coressponding to head
    if there was an incosistency, we remove the value from tail and return True
    :param csp: SudokuCSP instance
    :param t: tail
    :param h: head
    :param removals: removed domains
    :return: True if a value was removed
    """
    # Return True if we remove a value
    revised = False
    # If Xt=x conflicts with Xh=y for every possible y, eliminate Xt=x
    for x in csp.domains[Xt].copy():
        for y in csp.domains[Xh]:
            if not csp.conflicts(*Xt, x, *Xh, y):
                break
        else:
            csp.domains[Xt].remove(x)
            removals[Xt].add(x)
            revised = True
    return revised

def makeArcQue(csp, Xs):
    return [(Xt, Xh) for Xh in Xs for Xt in csp.adjList[Xh]]
