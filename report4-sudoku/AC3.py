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
        queue = [(t, x) for t in csp.adj_list for x in csp.adj_list[t]]
    # Queue of arcs of our concern
    while queue:
        # t is the tail of the arc
        # h is the head of the arc
        (t, h) = queue.pop()
        # check if we have inconsistency with other neighbours
        if remove_inconsistent_values(csp, t, h, removals):
            # if the domain became empty, then backtrack
            if not csp.domains[t]:
                return False
            elif len(csp.domains[t]) > 1:
                continue

            # add arcs (x, t) for nodes, adjacent to t
            for x in csp.adj_list[t]:
                if x != t:
                    queue.append((x, t))
    return True


def remove_inconsistent_values(csp, t, h, removals):
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
    for x in csp.domains[t].copy():
        for y in csp.domains[h]:
            if not csp.conflicts(*t, x, *h, y):
                break
        else:
            csp.domains[t].remove(x)
            removals[t].add(x)
            revised = True
    return revised


def make_arc_queue(csp, s):
    return [(t, h) for h in s for t in csp.adj_list[h]]
