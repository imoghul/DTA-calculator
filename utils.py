from numpy import mean


def average(x):
    if len(x) == 0: return 0
    return mean(x)


dtToMin = lambda y, mon, d, h, m, s: (525600 * y + 43800 * mon + 1440 * d + 60
                                      * h + m + s / 60)


def closestTo(arr, val):
    v = min(arr, key=lambda x: abs(x - val))
    return (v, arr.index(v))
