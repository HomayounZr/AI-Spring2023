from collections import defaultdict


def AC3(csp, queue=None, removals=defaultdict(set)):
    if queue is None:
        queue = [(t, h) for t in csp.adj_list for h in csp.adj_list[t]]

    while queue:
        # t: tail of the arc
        # h: head of the arc
        (t, h) = queue.pop()
        if remove_consisten_values(csp, t, h, removals):
            # domain beocmes empty -> no solution
            if not csp.domains[t]:
                return False

            elif len(csp.domains[t]) > 1:
                continue

            for X in csp.adj_list[t]:
                if X != t:
                    queue.append((X, t))
    return True


def remove_consisten_values(csp, t, h, removals):
    """return true if we remove a value"""
    revised = False
    for x in csp.domains[t].copy():
        for y in csp.domains[h]:
            if not csp.conflict(*t, x, *h, y):
                break

        else:
            csp.domains[t].remove(x)
            removals[t].add(x)
            revised = True
    return revised

def make_arc_queue(csp, Xs):
    return [(Xt, Xh) for Xh in Xs for Xt in csp.adj_list[Xh]]
