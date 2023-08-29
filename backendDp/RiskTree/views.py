import errno
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
    getAvgRiskP, getMinLocalSensitivityMap, keys2condition
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

    AttrMap = {
        'case1.csv': {
            'PrivateAttr': ['charges'],
            'ImplicitDescription': [],
            'NormalDescription': [],
            'ExplicitDescription': ['age', 'bmi', 'children'],
        },
        'case2.csv': {
            'PrivateAttr': ['Disease'],
            'ImplicitDescription': ['MentalH', 'GenH', ],
            'NormalDescription': ['SleepH'],
            'ExplicitDescription': ['BMI', 'PhysicalH', 'PhysicalA'],
        },
        'case3.csv': {
            'PrivateAttr': ['Income'],
            'ImplicitDescription': [],
            'NormalDescription': [],
            'ExplicitDescription': []
        },
    }
    # privateAttr = ['HeartDisease']
    # unusualAttr = ['BMI', 'PhysicalHealth', 'MentalHealth', 'PhysicalActivity', 'SleepTime']
    # privateAttr = ['Income']
    # unusualAttr = ['Year_Birth', 'Age_Customer']
    # privateAttr = ['charges']
    # unusualAttr = ['age', 'bmi', 'children']
    filename = file.name
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
                #     '80%' if attr in AttrMap[filename]['ExplicitDescription'] else
                # ('70%' if attr in AttrMap[filename]['NormalDescription'] else
                #  ('50%' if attr in AttrMap[filename]['ImplicitDescription'] else
                #  ('30%' if attr in AttrMap[filename]['PrivateAttr'] else '100%')))
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
                #     '80%' if attr in AttrMap[filename]['ExplicitDescription'] else
                # ('70%' if attr in AttrMap[filename]['NormalDescription'] else
                #  ('50%' if attr in AttrMap[filename]['ImplicitDescription'] else
                #  ('30%' if attr in AttrMap[filename]['PrivateAttr'] else '100%')))
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
    # 如果是第一次查询，那么将查看是否存在缓存
    if RiskRatioMap == -1:
        cachePath = 'RiskTree/cache/{0}/rt-{1}.cache.json'.format(filename.split('.')[0], filename)
        if os.path.exists(cachePath):
            with open(cachePath, 'r') as f:
                json_data = json.load(f)
        else:
            json_data = getRiskRecord(filename, attrList, indices, RiskRatioMap, DescriptionNum)
            if not os.path.exists(os.path.dirname(cachePath)):
                try:
                    os.makedirs(os.path.dirname(cachePath))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(cachePath, 'w+') as f:
                json.dump(json_data, f, cls=JsonEncoder)
    else:
        json_data = getRiskRecord(filename, attrList, indices, RiskRatioMap, DescriptionNum)

    #存入缓存

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

    cachePath = 'RiskTree/cache/{0}/dd-{1}.cache.json'.format(filename.split('.')[0], filename)
    if os.path.exists(cachePath):
        with open(cachePath, 'r') as f:
            ret = json.load(f)
    else:
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
                SearchRange = attr['Search Range'].split('~')
                Search_Min = float(SearchRange[0])
                Search_Max = float(SearchRange[1])
                Granularity = attr['Minimum Granularity']
                Tick_Values = [Search_Min + i * Granularity for i in range(100) if Search_Min + i * Granularity <= Search_Max]
                padding = (Search_Max - Search_Min) / 20
                ScaleData.append({
                    'name': attr['Name'],
                    'type': attr['Type'],
                    'domain': [Search_Min - padding, Search_Max + padding],
                    'Tick_Values': Tick_Values
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
            temp['data'] = list(set(temp['data']))  # 去重
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

        ret = {'ScaleData': ScaleData,
               'TableData': TableData,
               'TableKeyData': values,
               'MaxMap': MaxMap,
               'AttrsKeyMap': AttrsKeyMap}
        if not os.path.exists(os.path.dirname(cachePath)):
            try:
                os.makedirs(os.path.dirname(cachePath))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(cachePath, 'w+') as f:
            json.dump(ret, f, cls=JsonEncoder)

    return JsonResponse(ret, encoder=JsonEncoder)


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
    SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap = postData['SensitivityCalculationWay'], postData['AttrsKeyMap'], postData['BSTKeyMap']
    minSensitivityMap = postData['minSensitivityMap'] if attrParams['Type'] == 'numerical' and SensitivityCalculationWay == 'Local sensitivity' else 1
    avgRiskP = getAvgRiskP(filename, attr, attrParams, epsilon, attrOption, sensitivity, attrRisk, BSTMap, SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap, minSensitivityMap)
    return JsonResponse({'data': avgRiskP})


def initializeSchemeHistory(request):
    postData = json.loads(request.body)
    filename, attrOption = postData['filename'], postData['attrOption']
    attrList, epsilon = postData['attrList'],  postData['epsilon']
    BSTMap, attrRisk = postData['BSTMap'], postData['attrRisk']
    SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap = postData['SensitivityCalculationWay'], postData['AttrsKeyMap'], \
                                                        postData['BSTKeyMap']
    curAttr = postData['curAttr']
    avgRiskP = {}
    for attr, attrParams in zip(attrOption, attrList):
        if curAttr == attr:
            sensitivity = postData['sensitivity'][attr]
            avgRiskP = getAvgRiskP(filename, attr, attrParams, epsilon, attrOption, sensitivity, attrRisk, BSTMap,
                                   SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap)
    return JsonResponse({'data': avgRiskP})


def minSensitivityMap(request):
    postData = json.loads(request.body)
    filename, attrOption = postData['filename'], postData['attrOption']
    AttrsKeyMap, BSTKeyMap = postData['AttrsKeyMap'], postData['BSTKeyMap']
    attr = postData['attr']

    cachePath = 'RiskTree/cache/{0}/ms-{1}-{2}.cache.json'.format(filename.split('.')[0], filename, attr)
    if os.path.exists(cachePath):
        with open(cachePath, 'r') as f:
            ret = json.load(f)
    else:
        dfp = DFProcessor(filename, '', {}, 'Local sensitivity')
        minSensitivityMap = getMinLocalSensitivityMap(dfp, AttrsKeyMap, BSTKeyMap, attrOption, filename, attr,
                                                      attrOption.index(attr))
        ret = {'data': minSensitivityMap}
        with open(cachePath, 'w+') as f:
            json.dump(ret, f, cls=JsonEncoder)



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


def curHighRiskSQL(request):
    postData = json.loads(request.body)
    attrList, QueryAttr = postData['attrList'], postData['QueryAttr']
    index, attrIndex = postData['index'], postData['attrIndex']
    filename, attrOption = postData['filename'], postData['attrOption']
    AttrsKeyMap, BSTKeyMap = postData['AttrsKeyMap'], postData['BSTKeyMap']
    attrRiskMap, epsilon = postData['attrRiskMap'], postData['epsilon']
    deviation, privateVal = postData['deviation'], postData['privateVal']
    SensitivityCalculationWay, sensitivity = postData['SensitivityCalculationWay'], postData['sensitivity']
    # 让数据只读一次
    dfp = DFProcessor(filename, '', {}, 'Local sensitivity')
    if SensitivityCalculationWay == 'Local sensitivity':
        minSensitivityMap = getMinLocalSensitivityMap(dfp, AttrsKeyMap, BSTKeyMap, attrOption, filename, QueryAttr, attrIndex, index)
    else:
        minSensitivityMap = {}
        minSensitivityMap[index] = {
            'sensitivity': {},
            'firstSensitivityWay': {},
            'secondSensitivityWay': {},
            'minSensitivityDataIndices': {}
        }
        for dc in BSTKeyMap[str(index)]:
            dc_indices = dc['indices']
            if attrIndex in dc_indices:
                continue
            dc_keys = dc['keys']
            dcConditions, otherConditions = keys2condition(AttrsKeyMap, dc_indices, dc_keys)
            # 差分属性index

            for dcI in range(len(dc_indices)):
                secondQueryCondition = {}
                firstQueryCondition = {}
                for dc_index in dc_indices:
                    if dc_index == dc_indices[dcI]:
                        dcAttr = attrOption[dc_index]
                        secondQueryCondition[dcAttr] = otherConditions[dc_index]
                    else:
                        normalAttr = attrOption[dc_index]
                        firstQueryCondition[normalAttr] = [dcConditions[dc_index]]
                        secondQueryCondition[normalAttr] = [dcConditions[dc_index]]
                curBitmap = indices2bitmap(dc['indices'])
                dfp.resetParams(QueryAttr, secondQueryCondition)
                dataIndices = dfp.getCurDataIndices()
                if len(dataIndices) <= 1:
                    continue
                minSensitivityMap[index]['sensitivity'][curBitmap] = sensitivity
                minSensitivityMap[index]['firstSensitivityWay'][curBitmap] = firstQueryCondition.copy()
                minSensitivityMap[index]['secondSensitivityWay'][curBitmap] = secondQueryCondition.copy()
                minSensitivityMap[index]['minSensitivityDataIndices'][curBitmap] = dataIndices.copy()


    # 处理数据方便前端使用
    # 查找最小value的键
    compareVal = privateVal if SensitivityCalculationWay == 'Local sensitivity' else sensitivity
    sMap = minSensitivityMap[index]['sensitivity']
    bitmap = max(sMap,
                 key=lambda k: calcRiskP(sMap[k], max(sMap[k], compareVal), epsilon, deviation) * calcAttrRisk(
                     attrRiskMap, k))

    # 默认选用敏感度最大的那个
    minSensitivityMap[index]['sensitivity'] = minSensitivityMap[index]['sensitivity'][bitmap]
    minSensitivityMap[index]['firstSensitivityWay'] = minSensitivityMap[index]['firstSensitivityWay'][bitmap]
    minSensitivityMap[index]['secondSensitivityWay'] = minSensitivityMap[index]['secondSensitivityWay'][bitmap]
    minSensitivityMap[index]['minSensitivityDataIndices'] = minSensitivityMap[index]['minSensitivityDataIndices'][bitmap]
    return JsonResponse({'minSensitivityMap': minSensitivityMap[index]})