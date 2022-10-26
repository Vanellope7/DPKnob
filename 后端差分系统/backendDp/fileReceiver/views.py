import numpy as np
import pandas as pd
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from tools.utils import getHistogramData


def fileReceive(request):
    file = request.FILES.get('file')
    # 删除同名文件 虽然这样无法保留文件存档,但是可以确保传输端文件与接收端文件同名
    path = 'data/{}'.format(file)
    if default_storage.exists(path):
        default_storage.delete(path)
    storageTempPath = default_storage.save('data/{}'.format(file), ContentFile(file.read()))

    df = pd.read_csv(storageTempPath, sep=",")
    # 获取属性名列表供用户选择
    attr = df.columns.values
    # 获取直方图数据
    histData = getHistogramData(df)
    return JsonResponse({'attr': list(attr), 'data': histData})
