import json

from django.http import JsonResponse

from tools.StatisticsWithPrivacy import numericalStatistic, nonNumericalStatistic

def listorders(request):
    postData = json.loads(request.body)
    mech = postData['mechanism']
    res, privateRes = numericalStatistic(mech, postData) if postData['mechanismType'] == 'numerical' \
                 else nonNumericalStatistic(mech, postData)
    return JsonResponse({'privateRes': privateRes, 'res': res})