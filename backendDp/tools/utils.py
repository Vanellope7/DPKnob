


from tools.StatisticsWithPrivacy import StatisticsWithPrivacy
from tools.Laplace import Laplace


# 获取直方图数据 前端获取到该数据即可直接用D3画直方图
def getHistogramData(df, attr):
    a = df[attr].hist(bins=10)
    print(a)
    heights = [a.patches[i]._height for i in range(10)]
    width = a.patches[0]._width
    x0 = [a.patches[i].xy for i in range(10)]
    histData = [{'x0': x0[i][0], 'x1': x0[i][0] + width, 'height': heights[i]} for i in range(10)]
    return histData



def laplace_P(interval, b):
    L = Laplace(0, b)
    return L.laplace_F(interval[1]) - L.laplace_F(interval[0])

def binarySearch(left, right, precision, func, params, target):
    while right - left >= precision:
        mid = (left + right) / 2
        f = func(params, mid)
        if f > target:
            left = mid
        else:
            right = mid
    return round(mid, 5)
