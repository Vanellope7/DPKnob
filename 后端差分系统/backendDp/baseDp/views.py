import json

from django.http import JsonResponse
from utils import StatisticsWithPrivacy

def listorders(request):
    json_data = json.loads(request.body)
    mechanism = json_data['mechanism']  # 由于机制目前只有laplace机制,所以此参数暂时无用
    searchWay = json_data['searchWay']['way']
    params = json_data['searchWay']['params']
    filename = json_data['filename']
    epsilon = json_data['epsilon']

    # 为了封装性好一点，可以将这部分的一些代码封装到类里进行操作
    sp = StatisticsWithPrivacy(filename, epsilon)
    if searchWay == 'count':
        # 计算隐私值
        evalString_private = 'sp.private_{0}({1}, {2})'.format(searchWay, epsilon, params)
        privateRes = eval(evalString_private)
        # 计算真实值
        evalString = 'sp.{0}({1})'.format(searchWay, params)
        res = float(eval(evalString))
    else:
        # 计算隐私值
        evalString_private = 'sp.private_{0}({1})'.format(searchWay, epsilon)
        privateRes = eval(evalString_private)
        # 计算真实值
        evalString = 'sp.{0}()'.format(searchWay)
        res = float(eval(evalString))



    return JsonResponse({'privateRes': privateRes, 'res': res})