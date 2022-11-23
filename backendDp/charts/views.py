import json

import pandas as pd
from django.http import JsonResponse


from tools.utils import getHistogramData


def histogram(request):
    # 获取直方图数据
    postData = json.loads(request.body)
    df = pd.read_csv(postData['filename'], sep=",")
    domain = df[postData['attr']].max() - df[postData['attr']].min() + 1
    bins = 10
    histData = getHistogramData(df, postData['attr'], bins)
    return JsonResponse({'data': histData})