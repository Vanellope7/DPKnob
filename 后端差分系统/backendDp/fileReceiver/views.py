import json
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse

from utils import StatisticsWithPrivacy

def fileReceive(request):
    file = request.FILES.get('file')
    # 删除同名文件 虽然这样无法保留文件存档,但是可以确保传输端文件与接收端文件同名
    path = 'data/{}'.format(file)
    if default_storage.exists(path):
        default_storage.delete(path)
    storageTempPath = default_storage.save('data/{}'.format(file), ContentFile(file.read()))

    with open(storageTempPath, 'r', encoding="utf-8") as file:
        log_data = file.read()
        print(log_data)
    return JsonResponse({'res': True})