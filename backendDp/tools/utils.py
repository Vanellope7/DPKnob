import numpy as np

from tools.StatisticsWithPrivacy import StatisticsWithPrivacy
from tools.Laplace import Laplace


def getHistogramData(df, attr, bins):
    a = df[attr].hist(bins=bins)
    heights = [a.patches[i]._height for i in range(bins)]
    width = a.patches[0]._width
    x0 = [a.patches[i].xy for i in range(bins)]
    histData = [{'x0': x0[i][0], 'x1': x0[i][0] + width, 'height': heights[i]} for i in range(bins)]
    return histData


def laplace_P(interval, b):
    L = Laplace(b)
    return L.laplace_F(interval[1]) - L.laplace_F(interval[0])


def laplace_DV_P(interval, b):
    L = Laplace(b)
    p1 = L.Laplace_DV_F(interval[1])
    p2 = L.Laplace_DV_F(interval[0])
    return p1 - p2


def laplace_DP_f2(z, b1, b2):
    nz = -np.abs(z)
    return (1 / (4 * (b1 + b2))) * np.exp(nz / b1) + (1 / (4 * (b1 + b2))) * np.exp(nz / b2) \
                    + (1 / (4 * (b1 - b2))) * np.exp(nz / b1) - (1 / (4 * (b1 - b2))) * np.exp(nz / b2)


def laplace_DP_F2(z, b1, b2):
    nz = -np.abs(z)
    return 0.5 + 0.5 * np.sign(z) * (
                1 - ((b1 / (2 * (b1 + b2))) * np.exp(nz / b1) + (b2 / (2 * (b1 + b2))) * np.exp(nz / b2)
                     + (b1 / (2 * (b1 - b2))) * np.exp(nz / b1) - (b2 / (2 * (b1 - b2))) * np.exp(nz / b2)))


def laplace_DV_P2(interval, b1, b2):
    l, r = interval[0], interval[1]
    p1 = laplace_DP_F2(r, b1, b2)
    p2 = laplace_DP_F2(l, b1, b2)
    return p1 - p2


def binarySearch(left, right, precision, func, params, target):
    while right - left >= precision:
        mid = (left + right) / 2
        f = func(params, mid)
        flag = func(params, left) < func(params, right)
        if f < target:
            if flag:
                left = mid
            else:
                right = mid
        else:
            if flag:
                right = mid
            else:
                left = mid
    if abs(func(params, mid) - target) > precision:
        return False
    else:
        return round(mid, 5)


def ternarySearch(left, right, precision, func, params):
    while right - left >= precision:
        mid = (left + right) / 2
        mid_mid = (mid + right) / 2
        f1 = func(params, mid)
        f2 = func(params, mid_mid)
        if f1 >= f2:
            right = mid_mid
        else:
            left = mid
    return round(mid, 5)
