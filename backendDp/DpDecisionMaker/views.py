import json

from django.shortcuts import render

# Create your views here.
import numpy as np
from django.http import JsonResponse
from tools.utils import laplace_P, binarySearch, laplace_DV_P, ternarySearch, laplace_DV_P2


def UpdateEpsilonWithPrivacy(request):
    postData = json.loads(request.body)
    Sensitivity = postData['Sensitivity']
    isCount = postData['QueryType'] == 'count'
    d = postData['Deviation']  # 偏差值
    SRT = postData['SRT']  # 置信值
    curB1 = postData['b1']
    curB2 = postData['b2']
    attrRisk = postData['attrRisk']
    SRT /= attrRisk # 转化为攻击者成功概率
    left = 1e-200
    right = 1000000
    precision = 1e-5
    func = laplace_DV_P if curB1 == curB2 else lambda interval, b1: laplace_DV_P2(interval, b1, b1/curB1*curB2)  # 保持b1 和 b2 的比例关系
    if isCount:
        b = binarySearch(left, right, precision, func=func, params=[0, 0.5], target=SRT - 0.5)
    else:
        b = binarySearch(left, right, precision, func=func, params=[-d, d], target=SRT)
    if b == 0:
        b = 0.01
    epsilon = round(Sensitivity / b, 2)
    if curB1 != curB2:
        print('-----------------------------------------')
        print(SRT, laplace_DV_P2([-d, d], b, b/curB1*curB2))
    if curB1 == curB2:
        dp = laplace_DV_P([-d, d], curB1)  # deviation p
    else:
        dp = laplace_DV_P2([-d, d], curB1, curB2)
    return JsonResponse({'epsilon': epsilon, 'dp': dp})


def UpdateEpsilonWithAccuracy(request):
    postData = json.loads(request.body)
    Sensitivity = postData['Sensitivity']
    d = postData['Deviation']  # 偏差值
    SRT = postData['SRT']  # 置信值
    left = 1e-200
    right = 10000000
    precision = 1e-5
    curB = postData['b']
    isCount = postData['QueryType'] == 'count'
    b = binarySearch(left, right, precision, func=laplace_P, params=[-d, d], target=SRT)
    if b == 0:
        b = 0.01
    epsilon = round(Sensitivity / b, 2)

    # dp = laplace_P([-d, d], curB)  # deviation p
    return JsonResponse({'epsilon': epsilon})


def GetAccuracyDeviationP(request):
    postData = json.loads(request.body)
    b = postData['b']
    d = postData['Deviation']  # 偏差值
    dp = laplace_P([-d, d], b)  # deviation p
    return JsonResponse({'dp': float(dp)})


def GetPrivacyDeviationP(request):
    postData = json.loads(request.body)
    b1 = postData['b1']
    b2 = postData['b2']
    d = postData['Deviation']  # 偏差值
    func = (lambda interval, b1, b2: laplace_DV_P(interval, b1)) if b1 == b2 else lambda interval, b1, b2: laplace_DV_P2(interval, b1, b2)
    dp = func([-d, d], b1, b2)  # deviation p
    return JsonResponse({'dp': dp})
