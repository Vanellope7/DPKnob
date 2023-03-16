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
from RiskTree.NodeRiskFunc import getNodeRisk
from RiskTree.funcs import classifyAttr, getRiskRecord, getCubeByIndices, getDataCoder, key2string, indices2bitmap, \
    getAvgRiskP, getMinLocalSensitivityMap
from tools.df_processor import DFProcessor
from tools.utils import laplace_DV_P, laplace_DV_P2


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
    non_id_attr = attr # classifyAttr(df, attr) 区分非主键属性还存在缺陷 (像一些数值型数据的重复率也是0，无法判别，手动判别）
    for attr in non_id_attr:
        dtype = df[attr].dtype
        if dtype == 'object':
            # 非数值型
            Mode = df[attr].mode().tolist()[0]
            Range = df[attr].value_counts().index.tolist()
            AttrList.append({
                'Name': attr,
                'Type': 'categorical',
                'Range': Range,
                # 'Range Width': len(Range),
                'Search Range': '-',
                'Minimum Granularity': '-',
                'Leakage Probability': '100%'
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
                # 'Range Width': Max - Min,
                'Search Range': '{0}~{1}'.format(MinEdge, MaxEdge),
                'Minimum Granularity': width,
                'Leakage Probability': '100%'
            })
    return JsonResponse({'data': AttrList})


# 回应风险树数据请求
def riskTree(request):
    postData = json.loads(request.body)
    filename = postData['filename']
    attrList = postData['attrList']
    indices = postData['indices']
    DescriptionNum = postData['DescriptionNum']
    RiskRatioMap = postData.get('RiskRatioMap', -1)
    json_data = getRiskRecord(filename, attrList, indices, RiskRatioMap, DescriptionNum)
    return JsonResponse(json_data, encoder=JsonEncoder)


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
    indices = postData['indices']

    global m, DCs, R
    R = pd.read_csv('data/' + filename)

    keepAttr = list(map(lambda d: d['Name'], attrList))
    cur_keepAttr = [keepAttr[i] for i in indices]
    cur_attrList = [attrList[i] for i in indices]

    R = R[cur_keepAttr]
    R.fillna(0, inplace=True)
    n = R.shape[0]
    m = R.shape[1]

    start_time = time.time()
    DCs = getDataCoder(R, cur_attrList)
    getCodedData(R, DCs)

    values = R.values
    tree = {
        'index': list(range(n)),
        'key': 0,
        'pie': [0, n],
        'val': 0,
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
    m = R.shape[1]
    n = R.shape[0]
    DCs = getDataCoder(R, attrList)
    ScaleData = []

    for i, attr in enumerate(attrList):
        if attr['Type'] == 'numerical':
            padding = (DCs[i].params['Max'] - DCs[i].params['Min']) / 100
            ScaleData.append({
                'name': attr['Name'],
                'type': attr['Type'],
                'domain': [DCs[i].params['Min'] - padding, DCs[i].params['Max'] + padding]
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

    getCodedData(R, DCs)
    values = R.values
    AttrsKeyMap = []
    for d in range(m):
        temp = {'data': []}
        for i in range(n):
            temp['data'].append(values[i][d])
        temp['data'] = list(set(temp['data'])) # 去重
        temp['data'].sort()
        temp['text'] = list(map(lambda key: key2string(int(float(key)), DCs[d]), temp['data']))
        temp['type'] = DCs[d].type

        AttrsKeyMap.append(temp)

    MaxMap = {}
    for i, attr in enumerate(attrList):
        if attr['Type'] == 'numerical':
            MaxMap[attr['Name']] = DCs[i].params['Max']
        else:
            MaxMap[attr['Name']] = max(R[attr['Name']].value_counts().tolist())
    return JsonResponse({'ScaleData': ScaleData,
                         'TableData': TableData,
                         'TableKeyData': values,
                         'MaxMap': MaxMap,
                         'AttrsKeyMap': AttrsKeyMap},
                        encoder=JsonEncoder)


def getSensitivity(request):
    postData = json.loads(request.body)
    filename = postData['filename']
    attrs = postData['attrs']
    attrTypes = postData['attrTypes']
    sensitivityWay = postData['sensitivityWay']
    sensitivityMap = {}
    for i, attr in enumerate(attrs):
        type = attrTypes[i]
        dfp = DFProcessor(filename, attr, {}, sensitivityWay)
        sensitivity = dfp.getSumAndCountSens(type)
        sensitivityMap[attr] = {}
        sensitivityMap[attr]['sum'] = sensitivity[0]
        sensitivityMap[attr]['count'] = sensitivity[1]
    return JsonResponse({'sensitivityMap': sensitivityMap}, encoder=JsonEncoder)


def AvgRiskP(request):
    postData = json.loads(request.body)
    filename, attrOption = postData['filename'], postData['attrOption']
    attrParams, attr, epsilon = postData['attrParams'], postData['attr'], postData['epsilon']
    BSTMap, sensitivity, attrRisk = postData['BSTMap'], postData['sensitivity'], postData['attrRisk']
    minSensitivityMap = postData['minSensitivityMap']
    SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap = postData['SensitivityCalculationWay'], postData['AttrsKeyMap'], postData['BSTKeyMap']
    avgRiskP = getAvgRiskP(filename, attr, attrParams, epsilon, attrOption, sensitivity, attrRisk, BSTMap, SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap, minSensitivityMap)
    return JsonResponse({'data': avgRiskP})


def initializeSchemeHistory(request):
    postData = json.loads(request.body)
    filename, attrOption = postData['filename'], postData['attrOption']
    attrList, epsilon = postData['attrList'],  postData['epsilon']
    BSTMap, attrRisk = postData['BSTMap'], postData['attrRisk']
    SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap = postData['SensitivityCalculationWay'], postData['AttrsKeyMap'], \
                                                        postData['BSTKeyMap']
    ret = []
    for attr, attrParams in zip(attrOption, attrList):
        sensitivity = postData['sensitivity'][attr]
        avgRiskP = getAvgRiskP(filename, attr, attrParams, epsilon, attrOption, sensitivity, attrRisk, BSTMap,
                               SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap)
        # 计算 accuracy
        # b = sensitivity / epsilon
        # d = postData['Deviation']  # 偏差值
        # dp = laplace_P([-d, d], b)
        ret.append(avgRiskP)
    return JsonResponse({'data': ret})


def minSensitivityMap(request):
    postData = json.loads(request.body)
    attrList = postData['attrList']
    filename, attrOption = postData['filename'], postData['attrOption']
    AttrsKeyMap, BSTKeyMap = postData['AttrsKeyMap'], postData['BSTKeyMap']
    attr = postData['attr']
    # 让数据只读一次
    dfp = DFProcessor(filename, '', {}, 'Local sensitivity')
    minSensitivityMap = getMinLocalSensitivityMap(dfp, AttrsKeyMap, BSTKeyMap, attrOption, filename, attr, attrOption.index(attr))
    ret = {'data': minSensitivityMap}
    return JsonResponse(ret)


def calcRiskP(s1, s2, epsilon, deviation):
    if s1 == s2:
        p = laplace_DV_P([-deviation, deviation], s1 / epsilon)
    else:
        p = laplace_DV_P2([-deviation, deviation], s1 / epsilon, s2 / epsilon)
    return p


def calcAttrRisk(attrRiskMap, k):
    indices = getCubeByIndices(k)
    attrRisk = 1
    if attrRiskMap.get(str(k), -1) != -1:
        attrRisk = attrRiskMap[str(k)]
    else:
        for attrIndex in indices:
            attrRisk = min(attrRisk, attrRiskMap[str(1 << attrIndex)])
    return attrRisk


def curMinSensitivityMap(request):
    postData = json.loads(request.body)
    attrList, QueryAttr = postData['attrList'], postData['QueryAttr']
    index, attrIndex = postData['index'], postData['attrIndex']
    filename, attrOption = postData['filename'], postData['attrOption']
    AttrsKeyMap, BSTKeyMap = postData['AttrsKeyMap'], postData['BSTKeyMap']
    attrRiskMap, epsilon = postData['attrRiskMap'], postData['epsilon']
    deviation, privateVal = postData['deviation'], postData['privateVal']
    # 让数据只读一次
    dfp = DFProcessor(filename, '', {}, 'Local sensitivity')
    minSensitivityMap = getMinLocalSensitivityMap(dfp, AttrsKeyMap, BSTKeyMap, attrOption, filename, QueryAttr, attrIndex, index)

    # 处理数据方便前端使用
    # 查找最小value的键
    sMap = minSensitivityMap[index]['sensitivity']

    bitmap = max(sMap, key=lambda k: calcRiskP(sMap[k], max(sMap[k], privateVal), epsilon, deviation) * calcAttrRisk(
        attrRiskMap, k))
    # 默认选用敏感度最大的那个
    minSensitivityMap[index]['sensitivity'] = minSensitivityMap[index]['sensitivity'][bitmap]
    minSensitivityMap[index]['firstSensitivityWay'] = minSensitivityMap[index]['firstSensitivityWay'][bitmap]
    minSensitivityMap[index]['secondSensitivityWay'] = minSensitivityMap[index]['secondSensitivityWay'][bitmap]
    minSensitivityMap[index]['minSensitivityDataIndices'] = minSensitivityMap[index]['minSensitivityDataIndices'][bitmap]
    return JsonResponse({'minSensitivityMap': minSensitivityMap[index]})