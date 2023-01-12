import json

from django.shortcuts import render

# Create your views here.
import numpy as np
from django.http import JsonResponse
from tools.utils import laplace_P, binarySearch, laplace_DV_P, ternarySearch


def UpdateEpsilonWithPrivacy(request):
    postData = json.loads(request.body)
    Sensitivity = postData['Sensitivity']
    isCount = postData['QueryType'] == 'count'
    d = postData['Deviation']  # 偏差值
    SRT = postData['SRT']  # 置信值
    left = 1e-200
    right = 100
    precision = 1e-5
    if isCount:
        b = binarySearch(left, right, precision, func=laplace_DV_P, params=[0, 0.5], target=SRT - 0.5)
    else:
        b = binarySearch(left, right, precision, func=laplace_DV_P, params=[-d, d], target=SRT)
    epsilon = round(b / Sensitivity, 2)
    return JsonResponse({'epsilon': epsilon})


def UpdateEpsilonWithAccuracy(request):
    postData = json.loads(request.body)
    Sensitivity = postData['Sensitivity']
    d = postData['Deviation']  # 偏差值
    SRT = postData['SRT']  # 置信值
    left = 1e-200
    right = 100
    precision = 1e-5
    b = binarySearch(left, right, precision, func=laplace_P, params=[-d, d], target=SRT)
    epsilon = round(b / Sensitivity, 2)
    print(epsilon, Sensitivity)
    return JsonResponse({'epsilon': epsilon})


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
    mode = postData['mode']
    if mode == 'noise search':
        response = noiseSearch(postData)
    else:
        response = privacySearch(postData)
    return response


def noiseSearch(postData):
    d = postData['deviation']  # 偏差区间
    pd = postData['privacyScope']  # 隐私偏差区间
    cv = postData['confidenceVal']  # 置信值
    sameSign = np.sign(d[1]) == np.sign(d[0])
    if sameSign:
        # 区间同符号
        extremeP = 1 / (np.abs(np.log(np.abs(d[0])) - np.log(np.abs(d[1]))) / (np.abs(d[0] - d[1])))
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
        if res[0] == False:
            flag = 0
            res = []
        else:
            flag = 1
    testVal = []
    epsilon = []
    for r in res:
        if not r:
            break
        epsilon.append(1 / r)
        testVal.append(laplace_P(d, r))

    # 计算隐私偏差区间的置信值
    dvp = laplace_DV_P(pd, res[0] if len(res) > 0 else 1.0)
    print({'num': flag, 'val': res, 'epsilon': epsilon, 'testVal': testVal, 'dvp': dvp})


def privacySearch(postData):
    d = postData['deviation']  # 偏差区间
    pd = postData['privacyScope']  # 隐私偏差区间
    cv = postData['confidenceVal']  # 置信值
    sameSign = np.sign(pd[1]) == np.sign(pd[0])
    if sameSign:
        left = 1e-200
        right = 100
        precision = 1e-5
        extremeP = ternarySearch(left, right, precision, func=laplace_DV_P, params=pd)
        extreme = laplace_DV_P(pd, extremeP)  # 极值
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
            res1 = binarySearch(left, extremeP, precision, func=laplace_DV_P, params=pd, target=cv)
            res2 = binarySearch(extremeP, right, precision, func=laplace_DV_P, params=pd, target=cv)
            res = [res1, res2]
            flag = 2
    else:
        left = 1e-200
        right = 100
        precision = 1e-5
        res = [binarySearch(left, right, precision, func=laplace_DV_P, params=pd, target=cv)]
        if res[0] == False:
            flag = 0
            res = []
        else:
            flag = 1
    testVal = []
    epsilon = []
    for r in res:
        epsilon.append(1 / r)
        testVal.append(laplace_DV_P(pd, r))

    # 计算偏差区间的置信值
    p = [laplace_P(d, res[i]) for i in range(len(res))]
    return JsonResponse({'num': flag, 'val': res, 'epsilon': epsilon, 'testVal': testVal, 'p': p})