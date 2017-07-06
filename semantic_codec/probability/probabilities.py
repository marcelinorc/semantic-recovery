from math import fmod


def uniform(a, b):
    return 1 / (b-a)

def indep_intersection(probabilities):
    """
    Computes the intersection of independent events
    """
    p = 1
    for r in probabilities:
        p *= r
    return p


def indep_events_union(probabilities):
    """
    Computes the union of several independent events
    """
    result = 0
    # e cames from index 'estack' (which is how I pronounce 'stack' when speaking in Spanish) :)
    e = []
    if len(probabilities) == 0:
        raise RuntimeError('Probabilities list is empty')
    e.append(0)
    while e:  # while e is not empty
        p = 1
        for j in range(0, len(e)):
            p *= probabilities[e[j]]
        result = result + p if fmod(len(e), 2) == 1 else result - p

        i = e[len(e) - 1] + 1

        if i < len(probabilities):
            e.append(i)
        else:
            e.pop()
            if e:
                e[len(e) - 1] += 1

    return result
