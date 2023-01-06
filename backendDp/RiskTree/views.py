import json
import os
import time

import numpy as np
import pandas as pd
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse

from RiskTree.BSTTreeFunc import DFS, DFS_OUTER, getGap, getMinEdge, getMaxEdge
from RiskTree.BSTTreeFunc import getCodedData


# 回应接受文件请求
from RiskTree.Class import JsonEncoder
from RiskTree.funcs import classifyAttr, getRiskRecord, getCubeByIndices, getDataCoder, key2string


def fileReceive(request):
    file = request.FILES.get('file')
    # 删除同名文件 虽然这样无法保留文件存档,但是可以确保传输端文件与接收端文件同名
    path = 'data/{}'.format(file)
    print(path)
    if default_storage.exists(path):
        default_storage.delete(path)
    storageTempPath = default_storage.save('data/{}'.format(file), ContentFile(file.read()))

    df = pd.read_csv(storageTempPath)
    df.fillna(0, inplace=True)

    AttrList = []
    # 获取非ID属性名列表供用户选择
    attr = df.columns.tolist()
    non_id_attr = classifyAttr(df, attr)
    for attr in non_id_attr:
        dtype = df[attr].dtype
        if dtype == 'object':
            # 非数值型
            Mode = df[attr].mode().tolist()[0]
            AttrList.append({
                'Name': attr,
                'Type': 'nonnumerical',
                'Range': '-',
                'Range Width': '-',
                'Search Min Edge': '-',
                'DAable Window Width': '-',
                'Rounding Bit': '-'
            })
        else:
            # 数值型
            Mode = df[attr].mode().tolist()[0]
            Max = float(df[attr].max())
            Min = float(df[attr].min())
            width, bit = getGap(Min, Max)
            MinEdge = getMinEdge(width, Min)
            MaxEdge = getMaxEdge(width, MinEdge, Max)
            AttrList.append({
                'Name': attr,
                'Type': 'numerical',
                'Range': "{0}~{1}".format(Min, Max),
                'Range Width': Max - Min,
                'Search Min Edge': MinEdge,
                'Search Max Edge': MaxEdge,
                'DAable Window Width': width,
                'Rounding Bit': bit
            })

    return JsonResponse({'data': AttrList})


# 回应风险树数据请求
def riskTree(request):
    postData = json.loads(request.body)
    filename = postData['filename']
    attrList = postData['attrList']
    bitmap = postData['bitmap']
    json_data = getRiskRecord(filename, attrList, bitmap)
    return JsonResponse(json_data)


def QueryWheres(request):
    postData = json.loads(request.body)
    filename = postData['filename']
    attrList = postData['attrList']
    bitmap = postData['bitmap']
    R = pd.read_csv('data/' + filename)
    Indices = getCubeByIndices(bitmap)
    keepAttr = list(map(lambda d: d['Name'], attrList))
    cur_keepAttr = [keepAttr[i] for i in Indices]
    cur_attrList = [attrList[i] for i in Indices]
    R = R[cur_keepAttr]
    DCs = getDataCoder(R, cur_attrList)
    getCodedData(R, DCs)
    values = R.values
    n, m, GroupMap = R.shape[0], len(cur_keepAttr), {}
    for i in range(n):
        key = ""
        for j in range(m):
            key += str(values[i][j]) + '|'
        GroupMap[key] = GroupMap.get(key, [])
        GroupMap[key].append(i)
    json_data = []
    for key in GroupMap.keys():
        temp, splitKey = {}, key.split('|')
        for i, attr in enumerate(cur_keepAttr):
            temp[attr] = key2string(int(float(splitKey[i])), DCs[i])
        temp['key'] = key
        temp['num'] = len(GroupMap[key])
        temp['isBST'] = len(GroupMap[key]) == 1
        json_data.append(temp)
    json_data.sort(key=lambda d: d['num'])
    print(json_data)
    return JsonResponse({'data': json_data, 'attr': cur_keepAttr})


def BSTTree(request):
    postData = json.loads(request.body)
    filename = postData['filename']
    attrList = postData['attrList']
    bitmap = postData['bitmap']


    indices = getCubeByIndices(bitmap)


    global m, DCs, R
    R = pd.read_csv('data/' + filename)

    Indices = getCubeByIndices(bitmap)
    keepAttr = list(map(lambda d: d['Name'], attrList))
    cur_keepAttr = [keepAttr[i] for i in Indices]
    cur_attrList = [attrList[i] for i in Indices]

    R = R[cur_keepAttr]
    R.fillna(0, inplace=True)
    n = R.shape[0]
    m = R.shape[1]

    start_time = time.time()
    DCs = getDataCoder(R, cur_attrList)
    getCodedData(R, DCs)

    values = R.values
    tree = {
        'key': 0,
        'pie': [0, n],
        'children': DFS_OUTER(R.index.tolist(), 0, 0, 0, m, values)
    }
    keyMap = []
    for d in range(m):
        temp = {}
        temp['data'] = []
        for i in range(n):
            temp['data'].append(values[i][d])
        temp['data'] = list(set(temp['data'])) # 去重
        temp['data'].sort()
        temp['text'] = list(map(lambda key: key2string(int(float(key)), DCs[d]), temp['data']))
        temp['type'] = DCs[d].type

        keyMap.append(temp)


    end_time = time.time()
    run_time = end_time - start_time
    json_data = {
        'data': tree,
        'keyMap': keyMap,
        'run_time': run_time,
        'selectedAttr': cur_keepAttr,
        'Indices': indices
    }

    return JsonResponse(json_data, encoder=JsonEncoder)


def DataDistribution(request):
    postData = json.loads(request.body)
    filename = postData['filename']
    attrList = postData['attrList']
    R = pd.read_csv('data/' + filename)
    attrs = map(lambda d: d['Name'], attrList)
    R = R[attrs]
    R.fillna(0, inplace=True)
    DCs = getDataCoder(R, attrList)
    ScaleData = []
    for i, attr in enumerate(attrList):
        if attr['Type'] == 'numerical':
            ScaleData.append({
                'name': attr['Name'],
                'type': attr['Type'],
                'domain': [DCs[i].params['Min'], DCs[i].params['Max']]
            })
        else:
            ScaleData.append({
                'name': attr['Name'],
                'type': attr['Type'],
                'domain': list(DCs[i].params['map'].keys())
            })
    TableData = []
    for index, row in R.iterrows():
        TableData.append(row.to_dict())

    MaxMap = {}
    for i, attr in enumerate(attrList):
        if attr['Type'] == 'numerical':
            MaxMap[attr['Name']] = DCs[i].params['Max']
        else:
            MaxMap[attr['Name']] = max(R[attr['Name']].value_counts().tolist())
    return JsonResponse({'ScaleData': ScaleData, 'TableData': TableData, 'MaxMap': MaxMap})
