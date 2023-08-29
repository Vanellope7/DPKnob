import numpy as np

from utils.Laplace import Laplace


def laplace_DV_P(interval, b):
    L = Laplace(b)
    p1 = L.Laplace_DV_F(interval[1])
    p2 = L.Laplace_DV_F(interval[0])
    return p1 - p2


def laplace_DP_F2(z, b1, b2):
    nz = -np.abs(z)
    return 0.5 + 0.5 * np.sign(z) * (
                1 - ((b1 / (2 * (b1 + b2))) * np.exp(nz / b1) + (b2 / (2 * (b1 + b2))) * np.exp(nz / b2)
                     + (b1 / (2 * (b1 - b2))) * np.exp(nz / b1) - (b2 / (2 * (b1 - b2))) * np.exp(nz / b2)))


def laplace_DV_P2(interval, b1, b2):
    l, r = interval[0], interval[1]
    if b1 == b2:
        return laplace_DV_P([l, r], b1)
    p1 = laplace_DP_F2(r, b1, b2)
    p2 = laplace_DP_F2(l, b1, b2)
    return p1 - p2


def listIncluded(a, b):
    isInc = True
    if len(a) < len(b):
        a, b = b, a
    for v in b:
        if v not in a:
            isInc = False
    return isInc

