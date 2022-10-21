import json

from django.http import JsonResponse
from utils import StatisticsWithPrivacy

def listorders(request):
    json_data = json.loads(request.body)
    mechanism = json_data['mechanism']  # 由于机制目前只有laplace机制,所以此参数暂时无用
    searchWay = json_data['searchWay']
    epsilon = json_data['epsilon']
    sp = StatisticsWithPrivacy('animals_and_carrots.csv', 1.0)

    evalString_private = 'sp.private_{0}({1})'.format(searchWay, epsilon)
    evalString = 'sp.{0}()'.format(searchWay)
    print(evalString)
    res = float(eval(evalString))
    privateRes = eval(evalString_private)
    return JsonResponse({'privateRes': privateRes, 'res': res})