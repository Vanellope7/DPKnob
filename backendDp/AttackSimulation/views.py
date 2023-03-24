import json
import time

import numpy as np
from django.http import JsonResponse

from RiskTree.Class import JsonEncoder
from tools.df_processor import DFProcessor
from tools.Laplace import Laplace
from tools.utils import laplace_P, laplace_DV_P, laplace_DP_f2


def GetNoisyDataDistribution(request):
    postData = json.loads(request.body)

    dfp = DFProcessor(postData['FileName'], postData['QueryAttr'],
                      postData['QueryCondition'], postData['sensitivityWay'], postData['Interval'])

    res = float(eval("dfp.{0}()".format(postData['QueryType'])))
    sensitivities = dfp.getSensitivity(postData['QueryType'])
    sensitivity = dfp.getCurSensitivity(postData['QueryType'])

    b = float(sensitivity / postData['epsilon'])
    L = Laplace(b)
    D = []
    scope = [res - sensitivity * 2, res + sensitivity * 2] if postData['scope'] == -1 else postData['scope']
    for x in np.linspace(scope[0], scope[1], 1000):
        D.append([x, L.laplace_f(x - res)])
    ret = {'distribution': D, 'b': b, 'sensitivity': sensitivity, 'ExactVal': res, 'sensitivities': sensitivities, 'scope': scope}
    # 不是编码器的问题,就是返回了str  数据有问题才会返回字符串!!!! 比如 list里出现了不同类型的,以为浏览器也转型不了
    return JsonResponse(ret, encoder=JsonEncoder)


def GetPrivacyDistribution(request):
    postData = json.loads(request.body)
    b1 = postData['b1']
    b2 = postData['b2']
    scope = postData['scope']
    targetResult = postData['targetResult']

    ret = {}
    if scope == [-1, 2]:
        if targetResult == 0:
            p1 = laplace_DV_P([-0.5, 0], b1) + 0.5
            ret['deduceBar'] = [p1, 1-p1]
        elif targetResult == 1:
            p1 = laplace_DV_P([-0.5, 0], b1) + 0.5
            ret['deduceBar'] = [1-p1, p1]

    L = Laplace(b1)
    D = []
    dv_func = L.Laplace_DV_f if b1 == b2 else lambda d: laplace_DP_f2(d, b1, b2)
    for x in np.linspace(scope[0], scope[1], 1000):
        D.append([x, dv_func(x - targetResult)])
    ret['distribution'] = D
    return JsonResponse(ret)


def GetGeneralQueryDistribution(request):
    postData = json.loads(request.body)
    sensitivity = postData['sensitivity']
    epsilon = postData['epsilon']
    b = sensitivity / epsilon
    gapWidth = sensitivity * 1.2
    L = Laplace(b)
    D = []
    dv_func = L.laplace_f
    for x in np.linspace(-gapWidth, gapWidth, 1000):
        D.append([x, dv_func(x)])
    return JsonResponse({'distribution': D})


def GetOppositeProbability(request):
    postData = json.loads(request.body)
    b = postData['b']
    interval = postData['interval']
    ExactVal = postData['ExactVal']
    privacy = ExactVal['firstQuery'] - ExactVal['secondQuery']
    domainDeviation = postData['domainDeviation']

    firstRes, secondRes = [], []
    for x in np.linspace(-domainDeviation, domainDeviation, 1000):
        firstRes.append([x + ExactVal['firstQuery'], laplace_P([x + privacy - interval[1], x + privacy - interval[0]], b)])
        secondRes.append([x + ExactVal['secondQuery'], laplace_P([x - privacy + interval[0], x - privacy + interval[1]], b)])
    return JsonResponse({'firstRes': firstRes, 'secondRes': secondRes})

