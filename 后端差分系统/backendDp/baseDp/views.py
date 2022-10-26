import json

from django.http import JsonResponse
from tools.utils import getStatistics

def listorders(request):
    postData = json.loads(request.body)
    o = getStatistics(postData)
    return JsonResponse({'privateRes': o['privateRes'], 'res': o['res']})