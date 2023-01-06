import json

import numpy as np
from django.http import JsonResponse

from tools.df_processor import DFProcessor
from tools.Laplace import Laplace
from tools.utils import laplace_P


def GetNoisyDataDistribution(request):
    postData = json.loads(request.body)
    dfp = DFProcessor(postData['FileName'], postData['QueryAttr'])
    if postData['QueryType'] == 'count':
        res, sensitivity = eval("dfp.{0}({1})".format(postData['QueryType'], postData['Interval']))
    else:
        res, sensitivity = eval("dfp.{0}()".format(postData['QueryType']))
    b = sensitivity / postData['epsilon']
    L = Laplace(b)
    D = []
    for x in np.linspace(-sensitivity, sensitivity, 1000):
        D.append([x + res, L.laplace_f(x)])
    return JsonResponse({'distribution': D, 'b': b, 'sensitivity': sensitivity, 'ExactVal': res})


def GetPrivacyDistribution(request):
    postData = json.loads(request.body)
    b = postData['b']
    targetResult = postData['targetResult']
    L = Laplace(b)
    D = []
    for x in np.linspace(-2 * targetResult, 2 * targetResult, 1000):
        D.append([x + targetResult, L.Laplace_DV_f(x)])
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


def getHOPsData(request):
    postData = json.loads(request.body)
    # res, privateRes = numericalStatistic(mech, postData) if postData['mechanismType'] == 'numerical' \
    #              else nonNumericalStatistic(mech, postData)

    # 计算第一次查询的HOPs绘图数据
    dfp = DFProcessor(postData['filename'], postData['attr'])
    firstRes, sensitivity = eval("dfp.{0}()".format(postData['way']))
    mu, b = postData['mu'], sensitivity / postData['epsilon']
    firstPrivateRes = np.random.laplace(mu, b, 1000) + firstRes

    # 计算第二次查询的HOPs绘图数据
    privacy = postData['privacy']
    secondRes = firstRes - privacy
    print(firstRes, '---------------')
    print(secondRes)
    secondPrivateRes = np.random.laplace(mu, b, 1000) + secondRes

    privacyRes = firstPrivateRes - secondPrivateRes

    return JsonResponse({
        'firstQuery': {
            'privateRes': list(firstPrivateRes), 'res': float(firstRes),
        },
        'secondQuery': {
            'privateRes': list(secondPrivateRes), 'res': float(secondRes),
        },
        'DA': {
            'privateRes': list(privacyRes), 'res': float(privacy),
        },
        'b': b
    })

