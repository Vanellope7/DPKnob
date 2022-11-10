import json

from django.shortcuts import render

# Create your views here.
import numpy as np
from django.http import JsonResponse
from tools.utils import laplace_P, binarySearch

def getEpsilon(request):
    """
    通过偏差区间和置信值求拉普拉斯分布的参数b, 默认u = 0

    Parameters
    ----------
    request : post request containing post data
        内含参数:
            deviation : 偏差区间, 也即概率区间
            confidenceVal : 置信值, 也即概率
    """
    postData = json.loads(request.body)
    d = postData['deviation']            # 偏差区间
    cv = postData['confidenceVal']       # 置信值
    sameSign = np.sign(d[0]) == np.sign(d[1])
    if sameSign:
        # 区间同符号
        extremeP = 1 / (np.log(np.abs(d[0]) / np.abs(d[1])) / (np.abs(d[0]) - np.abs(d[1])))
        extreme = laplace_P(d, extremeP)
        if extreme < cv:
            flag = 0
            res = []
        elif extreme == cv:
            res = [extremeP]
            flag = 1
        else:
            left = 1e-200
            right = 100
            precision = 1e-5
            res1 = binarySearch(left, extremeP, precision, func=laplace_P, params=d, target=cv)
            res2 = binarySearch(extremeP, right, precision, func=laplace_P, params=d, target=cv)
            res = [res1, res2]
            flag = 2
    else:
        left = 1e-200
        right = 100
        precision = 1e-5
        res = [binarySearch(left, right, precision, func=laplace_P, params=d, target=cv)]
        flag = 1

    return JsonResponse({'num': flag, 'val': res})
