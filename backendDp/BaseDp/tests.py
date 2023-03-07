<<<<<<< HEAD
from django.test import TestCase

# Create your tests here.
=======
import math

import numpy as np

from tools.Laplace import Laplace
from tools.utils import laplace_DV_P2, laplace_DV_P, laplace_P

# 验证b1 b2 交换无差别
x = -1
y = 1
b1 = 100
b2 = 200
p1 = laplace_DV_P2([x, y], b1, b2)
p2 = laplace_DV_P2([x, y], b2, b1)
# print(p1, p2)
print(laplace_P([x, y], b1))
print(laplace_DV_P([x, y], b1))

# 验证公式正确性
# data1 = np.random.laplace(0, b1, 10000000)
# data2 = np.random.laplace(0, b2, 10000000)
# dv = data1 - data2
# p1 = (len(dv[dv < y]) - len(dv[dv < x])) / len(dv)
#
#
# def func(z):
#     x = (b1 / (4 * (b1 + b2))) * math.exp(z/b1) + (b2 / (4 * (b1 + b2))) * math.exp(z/b2) \
#             + (b1 / (4 * (b1 - b2))) * math.exp(z / b1) - (b2 / (4 * (b1 - b2))) * math.exp(z/b2)
#     return x
#
#
#
# p2 = laplace_DV_P2([x, y], b1, b2)
# print(p1, p2)
#
# def x(a, b, c):
#     print(a, b, c)
# f = lambda d: x(d, 2, 2)
# f(2)
# f(3)
>>>>>>> ec03867 (initial)
