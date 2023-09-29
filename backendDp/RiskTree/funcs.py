# 接收文件，返回数据
import itertools
import math
import time
from collections import defaultdict
from functools import reduce

import numpy as np
import pandas as pd

from RiskTree.Class import DataCoder
from RiskTree.NodeRiskFunc import getNodeRisk, getChildNodeRiskRatio
from tools.df_processor import DFProcessor
from tools.utils import laplace_DV_P, laplace_DV_P2


def key2string(key, DataCoder):
    type = DataCoder.type
    params = DataCoder.params
    if type == 'numerical':
        Min, Width = params['Min'], params['Width']
        ret = "{0}~{1}".format(Min + Width * key, Min + Width * key + Width)
    else:
        ret = params['rmap'][key]
    return ret


def classifyAttr(df, attrs):
    non_id_attr = []
    n = df.shape[0]
    for i, attr in enumerate(attrs):
        if attr == 'Cabin':
            continue
        if df[attr].duplicated().sum() > 0.5 * n:
            non_id_attr.append(attr)
    return non_id_attr


def isWithinDepth(x, depth):
    indices = getCubeByIndices(x)
    return len(indices) <= depth


def getChildrenMap(Lattice):
    n = len(Lattice)
    ret = {}
    for i in range(n):
        for j in range(i + 1, n):
            x, y = Lattice[i], Lattice[j]
            if x & y == 0:
                ret[x + y] = ret.get(x + y, [])
                ret[x + y].append(x)
                ret[x + y].append(y)
    return ret


def ConstructLattice(bitmap, m):
    indices = getCubeByIndices(bitmap)
    dimensions = [i for i in range(m) if i not in indices]
    lattice = [bitmap + (1 << dimension) for dimension in dimensions]
    return lattice


def getDataCoder(data, attrList):
    gap, step = 1, 1
    columns = data.columns.tolist()
    DCs = []
    for (i, column) in enumerate(columns):
        # 首先得知道数据的范围
        type = attrList[i]['Type']
        if type == 'numerical':
            Width = attrList[i]['Query granularity']
            splitEdge = attrList[i]['Search Range'].split('~')
            MinEdge = float(splitEdge[0])
            MaxEdge = float(splitEdge[1])
            Width = float(Width) if isinstance(Width, str) else Width
            MaxEdge = float(MaxEdge) if isinstance(MaxEdge, str) else MaxEdge
            MinEdge = float(MinEdge) if isinstance(MinEdge, str) else MinEdge
            params = {
                'Min': MinEdge,
                'Max': MaxEdge,
                'Width': Width,
            }
            DC = DataCoder(type, params)
            DCs.append(DC)
        else:
            category_map = {}
            category_rmap = {}
            categories = list(set(data[column].tolist()))
            categories.sort() # 这里需要统一，已经发现了这里常常多次运行时不统一导致出现问题
            for (index, category) in enumerate(categories):
                category_map[category] = index
                category_rmap[index] = category
            DC = DataCoder(type, {'map': category_map, 'rmap': category_rmap})
            DCs.append(DC)
    return DCs


def getCubeByIndices(x):
    i = 0
    indices = []
    while x:
        c = x & 1
        if c == 1:
            indices.append(i)
        i += 1
        x = x >> 1
    return indices


def GenerateCandidateTupleIndex(n):
    # 本来是用来剪枝的,但是交互模式更改后就不需要剪枝了
    CandidateTuple = range(n)
    return CandidateTuple


def getCodedData(data, DCs, attrs, sensitivityAttr=''):
    columns = attrs
    for rowI in range(len(data)):
        for i, column in enumerate(columns):
            if column != sensitivityAttr:
                data[rowI][i] = DCs[i].enCoder(data[rowI][i])


def BFS(values, lattice, n):
    BSTMap = {}
    RiskRatioMap = {}
    for q in lattice:
        GroupMap = {}
        indices = getCubeByIndices(q)
        candidateTuple = GenerateCandidateTupleIndex(n)
        for i in candidateTuple:
            key = ""
            for j in indices:
                key += str(values[i][j]) + '|'
            GroupMap[key] = GroupMap.get(key, [])
            GroupMap[key].append(i)

        BSTMap[q] = set()
        for key in GroupMap.keys():
            if len(GroupMap[key]) == 1:
                index = GroupMap[key][0]
                BSTMap[q].add(index)
        RiskRatioMap[q] = [len(BSTMap[q]), len(GroupMap)]
    return BSTMap, RiskRatioMap


def makeTree(indices, m, bitmap, RiskRatioMap, childNodeRiskRatio):
    # print(BSTMap)
    ret = []
    dimensions = [i for i in range(m) if i not in indices]
    for dimension in dimensions:
        new_bitmap = bitmap + (1 << dimension)
        ret.append({
            'indices': indices + [dimension],
            'name': new_bitmap,
            'childNodeRiskPie': childNodeRiskRatio[new_bitmap],
            'curNodeRiskPie': RiskRatioMap[str(new_bitmap)],
            'children': [],
            'val': 1
        })
    return ret


def indices2bitmap(indices):
    ret = 0
    for index in indices:
        ret += 1 << index
    return ret


def getRiskRecord(filename, attrList, indices, RiskRatioMap, DescriptionNum):
    R = pd.read_csv('data/{0}'.format(filename))
    keepAttr = map(lambda d: d['Attribute'], attrList)
    BSTMap = {}
    BSTKeyMap = defaultdict(list)
    R = R[keepAttr]
    R.fillna(0, inplace=True)
    n = R.shape[0]
    m = R.shape[1]
    attrs = R.columns.tolist()
    bitmap = indices2bitmap(indices)
    start_time = time.time()
    DCs = getDataCoder(R, attrList)
    values = R.values
    getCodedData(values, DCs, attrs)

    lattice = ConstructLattice(bitmap, m)
    riskRecord = set()
    if RiskRatioMap == -1:
        BSTMap, BSTKeyMap, RiskRatioMap, riskRecord = getNodeRisk(values, DescriptionNum)  # 遍历了全部记录
    # riskRecord = list(riskRecord)
    # childNodeRiskRatio = getChildNodeRiskRatio(lattice, RiskRatioMap, m, DescriptionNum)
    # print(RiskRatioMap, '\n', childNodeRiskRatio)
    # tree = {
    #     'indices': indices,
    #     'name': bitmap,
    #     'childNodeRiskPie': [0, 0],
    #     'curNodeRiskPie': [0, n],
    #     'children': makeTree(indices, m, bitmap, RiskRatioMap, childNodeRiskRatio)
    # }
    # end_time = time.time()
    # run_time = end_time - start_time

    # BST内的set转list
    for key in BSTMap.keys():
        BSTMap[key] = list(BSTMap[key])

    json_data = {
        # 'treeData': tree,
        # 'run_time': run_time,
        'Indices': indices,
        'RiskRatioMap': RiskRatioMap,
        'BSTMap': BSTMap,
        'BSTKeyMap': BSTKeyMap,
        'riskRecord': list(riskRecord)
    }
    return json_data


def keys2condition(AttrsKeyMap, dc_indices, dc_keys):
    conditions = {}
    otherConditions = {}
    conditionKeyMap = {}
    for dc_index, dc_key in zip(dc_indices, dc_keys):
        conditionKeyMap[dc_index] = {}
        keyMap = AttrsKeyMap[dc_index]
        keys, texts, type = keyMap['data'], keyMap['text'], keyMap['type']
        dc_text = texts[keys.index(int(float(dc_key)))]
        if type == 'numerical':
            conditions[dc_index] = tuple(map(lambda d: float(d), dc_text.split('~')))
            otherConditions[dc_index] = [tuple(map(lambda d: float(d), text.split('~'))) for text in texts if
                                         text != dc_text]
        else:
            conditions[dc_index] = dc_text
            otherConditions[dc_index] = [text for text in texts if text != dc_text]
    return conditions, otherConditions


def getConditionKeyMap(AttrsKeyMap):
    ConditionKeyMap = {}
    for index in range(len(AttrsKeyMap)):
        ConditionKeyMap[index] = {}
        attrType = AttrsKeyMap[index]['type']
        for key, text in zip(AttrsKeyMap[index]['data'], AttrsKeyMap[index]['text']):
            condition = tuple(map(lambda d: float(d), text.split('~'))) if attrType == 'numerical' else text
            ConditionKeyMap[index][condition] = key
    return ConditionKeyMap


def getMinLocalSensitivityMap(dfp, AttrsKeyMap, BSTKeyMap, attrOption, filename, attr, attrIndex, index=-1, ):
    minSensitivityMap = {}
    group = BSTKeyMap.keys() if index == -1 else [str(index)]
    conditionKeyMap = getConditionKeyMap(AttrsKeyMap)
    codeSensitivityMap = {}
    for bstIndex in group:
        minSensitivityDict = {}
        firstSensitivityWayDict = {}
        secondSensitivityWayDict = {}
        minSensitivityDataIndicesDict = {}
        # differencing condition
        for dc in BSTKeyMap[bstIndex]:
            minSensitivity = float('inf')
            firstSensitivityWay = {}
            secondSensitivityWay = {}
            minSensitivityDataIndices = []
            dc_indices = dc['indices']
            if attrIndex in dc_indices:
                continue
            dc_keys = dc['keys']
            dcConditions, otherConditions = keys2condition(AttrsKeyMap, dc_indices, dc_keys)

            # 选定不同的属性作为差分条件时
            for dc_index, dc_key in zip(dc_indices, dc_keys):
                normalCondition = [(index, dcConditions[index]) for index in dc_indices if index != dc_index]
                normalAttr = [attrOption[index] for index in dc_indices if index != dc_index]
                dcCondition = otherConditions[dc_index]

                dcAttr = attrOption[dc_index]
                # 这里考虑的是一个【属性条件】不同 其他相同的情况
                for dcc in dcCondition:
                    secondQueryCondition = {dcAttr: [dcc]}
                    firstQueryCondition = {dcAttr: [dcc, dcConditions[dc_index]]}
                    codeList = ['{0}-{1}'.format(dcAttr, conditionKeyMap[dc_index][dcc])]
                    for n_attr, (index, condition) in zip(normalAttr, normalCondition):
                        secondQueryCondition[n_attr] = [condition]
                        firstQueryCondition[n_attr] = [condition]
                        codeList.append('{0}-{1}'.format(n_attr, conditionKeyMap[index][condition]))
                    code = '*'.join(codeList)
                    if codeSensitivityMap.get(code, -1) == -1:
                        dfp.resetParams(attr, secondQueryCondition)
                        sensitivity = dfp.getCurSensitivity('sum')
                        if sensitivity == 'None':
                            continue
                        dataIndices = dfp.getCurDataIndices()
                        codeSensitivityMap[code] = {
                            'sensitivity': sensitivity,
                            'dataIndices': dataIndices
                        }
                    else:
                        sensitivity = codeSensitivityMap.get(code)['sensitivity']
                        dataIndices = codeSensitivityMap.get(code)['dataIndices']
                    if sensitivity == 'None':
                        continue
                    else:
                        if minSensitivity > sensitivity:
                            minSensitivity = sensitivity
                            firstSensitivityWay = firstQueryCondition.copy()
                            secondSensitivityWay = secondQueryCondition.copy()
                            minSensitivityDataIndices = dataIndices.copy()
                # 对于三属性的还有一种情况是 一个【属性条件】相同  其他不同的情况 这里进行补充，3属性以上不考虑

                # if len(dc_indices) == 3:
                #     curNormalCondition = dcConditions[dc_index]
                #     curDcConditions = [(index, otherConditions[index]) for index in dc_indices if index != dc_index]
                #     i1, dcc1s = curDcConditions[0]
                #     for dcc1 in dcc1s:
                #         attr1 = attrOption[i1]
                #         normal_dcc1 = dcConditions[i1]
                #         secondQueryCondition = {dcAttr: [curNormalCondition]}
                #         firstQueryCondition = {dcAttr: [curNormalCondition]}
                #         codeList = ['{0}-{1}'.format(dcAttr, curNormalCondition)]
                #         secondQueryCondition[attr1] = [dcc1]
                #         firstQueryCondition[attr1] = [dcc1, normal_dcc1]
                #         codeList.append('{0}-{1}'.format(attr1, conditionKeyMap[i1][dcc1]))
                #         i2, dcc2s = curDcConditions[1]
                #         for dcc2 in dcc2s:
                #             temp = codeList.copy()
                #             attr2 = attrOption[i2]
                #             normal_dcc2 = dcConditions[i2]
                #             secondQueryCondition[attr2] = [dcc2]
                #             firstQueryCondition[attr2] = [dcc2, normal_dcc2]
                #             temp.append('{0}-{1}'.format(attr2, conditionKeyMap[i2][dcc2]))
                #
                #             code = '*'.join(temp)
                #             if codeSensitivityMap.get(code, -1) == -1:
                #                 dfp.resetParams(attr, secondQueryCondition)
                #                 sensitivity = dfp.getCurSensitivity('sum')
                #                 if sensitivity == 'None':
                #                     continue
                #                 dataIndices = dfp.getCurDataIndices()
                #                 codeSensitivityMap[code] = {
                #                     'sensitivity': sensitivity,
                #                     'dataIndices': dataIndices
                #                 }
                #             else:
                #                 sensitivity = codeSensitivityMap.get(code)['sensitivity']
                #                 dataIndices = codeSensitivityMap.get(code)['dataIndices']
                #             if sensitivity == 'None':
                #                 continue
                #             else:
                #                 if minSensitivity > sensitivity:
                #                     minSensitivity = sensitivity
                #                     firstSensitivityWay = firstQueryCondition.copy()
                #                     secondSensitivityWay = secondQueryCondition.copy()
                #                     minSensitivityDataIndices = dataIndices.copy()

            bitmap = indices2bitmap(dc['indices'])
            minSensitivityDict[bitmap] = 99999999 if minSensitivity == float('inf') else minSensitivity
            firstSensitivityWayDict[bitmap] = firstSensitivityWay
            secondSensitivityWayDict[bitmap] = secondSensitivityWay
            minSensitivityDataIndicesDict[bitmap] = minSensitivityDataIndices

        minSensitivityMap[int(bstIndex)] = {
            'sensitivity': minSensitivityDict,
            'firstSensitivityWay': firstSensitivityWayDict,
            'secondSensitivityWay': secondSensitivityWayDict,
            'minSensitivityDataIndices': minSensitivityDataIndicesDict
        }
    return minSensitivityMap


# def getMinLocalSensitivity(attrR):
#     s = attrR.nsmallest(2)
#     return float(s.values[1])


def getAvgRiskP(filename, attr, attrParams, epsilon, attrOption, sensitivity, attrRisk, BSTMap,
                SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap, minSensitivityMap=None):
    if minSensitivityMap is None:
        minSensitivityMap = {}
    R = pd.read_csv('data/{0}'.format(filename))
    R.fillna(0, inplace=True)
    attrR = R[attr]
    attrIndex = attrOption.index(attr)
    barData = {}
    maxRiskRecordMap = {}

    # query2S = 0
    # if SensitivityCalculationWay == 'Local sensitivity' and getNewMinSensitivity:
    #     minSensitivityMap = getMinLocalSensitivityMap(AttrsKeyMap, BSTKeyMap, attrOption, filename, attr)

    if attrParams['Type'] != 'numerical':  # 类别型数据
        attackRisk = laplace_DV_P([0, 0.5], sensitivity['count'] / epsilon) + 0.5
        sumRisk = 0
        countRiskList = []
        countBarChart = {}
        for i in range(10):
            countBarChart[i] = 0
        cnt = 0
        curCountRisk = 0
        countRiskMap = {}
        countMaxRiskRecord = defaultdict(int)
        countConditionMap = {}
        for bitmap in BSTMap:
            indices = getCubeByIndices(int(bitmap))
            if attrIndex in indices:
                continue
            for index in BSTMap[bitmap]:
                minAttrRiskP = 1
                if attrRisk.get(str(bitmap), -1) != -1:
                    minAttrRiskP = attrRisk[str(bitmap)]
                else:
                    for attrI in indices:
                        minAttrRiskP = min(minAttrRiskP, attrRisk[str(1 << attrI)])
                if attackRisk * minAttrRiskP >= countMaxRiskRecord[index]:
                    countMaxRiskRecord[index] = attackRisk * minAttrRiskP
                    countConditionMap[index] = {
                        'indices': indices,
                        'bitmap': bitmap
                    }
        for index, p in countMaxRiskRecord.items():
            if p > curCountRisk:
                curCountRisk = p
                countRiskMap['index'] = index
                countRiskMap['risk'] = p
                countRiskMap['condition'] = countConditionMap[index]
            sumRisk += p
            countRiskList.append(p)
            cnt += 1
        for countRisk in countRiskList:
            key = min(math.floor(countRisk * 100) // 10, 9)
            if round(countRisk, 2) != 1 and (round(countRisk, 2) * 100) % 10 == 0 and key >= 1:
                key -= 1
            countBarChart[key] += 1
        for i in range(10):
            countBarChart[i] /= len(countRiskList)
        return {'sum': '-', 'count': [attackRisk, sumRisk / cnt, list(countBarChart.values())],  'maxRiskRecordMap': maxRiskRecordMap, 'countMaxRiskRecord': countRiskMap}
    else:  # 数值型数据
        riskRank = {}
        sumRet = {'avgRiskList': [], 'attackRiskList': []}
        for deviationRatio in np.linspace(0.1, 1, 10):
            ratioStr = str(round(deviationRatio, 1))
            maxRiskRecordMap[ratioStr] = {
                'index': -1,
                'risk': 0,
                'condition': {}
            }
            riskRank[ratioStr] = []
            pMap = defaultdict(int)
            attackPMap = defaultdict(int)
            conditionMap = defaultdict(dict)
            riskNum = 0
            for i in range(10):
                barData[i] = 0
            for bitmap in BSTMap:
                indices = getCubeByIndices(int(bitmap))
                if attrIndex in indices:
                    continue
                for index in BSTMap[bitmap]:

                    minAttrRiskP = 1
                    # deviation = sensitivity['sum'] * deviationRatio
                    deviation = attrR[index] * deviationRatio
                    if SensitivityCalculationWay == 'Local sensitivity':
                        query1S = max(minSensitivityMap[str(index)]['sensitivity'][str(bitmap)], attrR[index])
                        query2S = minSensitivityMap[str(index)]['sensitivity'][str(bitmap)]
                        if query1S == query2S:
                            p = laplace_DV_P([-deviation, deviation], query1S / epsilon)
                        else:
                            p = laplace_DV_P2([-deviation, deviation], query1S / epsilon, query2S / epsilon)
                    else:
                        p = laplace_DV_P([-deviation, deviation], sensitivity['sum'] / epsilon)
                    if p * minAttrRiskP >= pMap[index]:
                        pMap[index] = p * minAttrRiskP
                        attackPMap[index] = p * minAttrRiskP
                        conditionMap[index] = {
                            'indices': indices,
                            'bitmap': bitmap
                        }
            for index, p in attackPMap.items():
                riskRank[ratioStr].append({
                    'index': index,
                    'risk': p,
                    'condition': conditionMap[index]
                })
                if p > maxRiskRecordMap[ratioStr]['risk']:
                    maxRiskRecordMap[ratioStr]['index'] = index
                    maxRiskRecordMap[ratioStr]['risk'] = p
                    maxRiskRecordMap[ratioStr]['condition'] = conditionMap[index]
                key = min(math.floor(p * 100) // 10, 9)

                if round(p, 2) != 1 and(round(p, 2) * 100) % 10 == 0 and key >= 1:
                    key -= 1
                barData[key] += 1
                riskNum += 1
            maxRiskRecordMap[ratioStr] = riskRank[ratioStr][9]
            riskRank[ratioStr].sort(key=lambda d: -d['risk'])
            sumRet['avgRiskList'].append(math.fsum(pMap.values()) / len(pMap))
            sumRet['attackRiskList'].append(list(map(lambda d: d / riskNum, barData.values())))

        # 求count的结果
        attackRisk = laplace_DV_P([0, 0.5], sensitivity['count'] / epsilon) + 0.5
        sumRisk = 0
        cnt = 0
        countRiskList = []
        countBarChart = {}
        for i in range(10):
            countBarChart[i] = 0
        cnt = 0
        curCountRisk = 0
        countRiskMap = {}
        countMaxRiskRecord = defaultdict(int)
        countConditionMap = {}
        for bitmap in BSTMap:
            indices = getCubeByIndices(int(bitmap))
            if attrIndex in indices:
                continue
            for index in BSTMap[bitmap]:
                minAttrRiskP = 1
                if attackRisk * minAttrRiskP >= countMaxRiskRecord[index]:
                    countMaxRiskRecord[index] = attackRisk * minAttrRiskP
                    countConditionMap[index] = {
                        'indices': indices,
                        'bitmap': bitmap
                    }
        for index, p in countMaxRiskRecord.items():
            if p > curCountRisk:
                curCountRisk = p
                countRiskMap['index'] = index
                countRiskMap['risk'] = p
                countRiskMap['condition'] = countConditionMap[index]
            sumRisk += p
            countRiskList.append(p)
            cnt += 1
        for countRisk in countRiskList:
            key = min(math.floor(countRisk * 100) // 10, 9)
            if round(countRisk, 2) != 1 and (round(countRisk, 2) * 100) % 10 == 0 and key >= 1:
                key -= 1
            countBarChart[key] += 1
        for i in range(10):
            countBarChart[i] /= len(countRiskList)
        return {'sum': sumRet, 'count': [attackRisk, sumRisk / cnt, list(countBarChart.values())], 'maxRiskRecordMap': maxRiskRecordMap, 'countMaxRiskRecord': countRiskMap, 'riskRank': riskRank}


def Attack2RiskMap(values, Attack, attrParams, epsilon):
    # 求sum的结果
    sumRet = {'attackRiskList': [], 'avgRiskList': [0 for i in range(10)]}
    ARL = sumRet['attackRiskList']
    AttackNum = sum([len(ats) for ats in Attack.values()])
    if attrParams['Type'] == 'numerical':
        for deviationRatio in np.linspace(0.1, 1, 10):
            temp = [0 for i in range(10)]
            for ats in Attack.values():

                for at in ats:
                    pvi = int(at[0])
                    if pvi == 543:
                        print('xxx')
                    D = values[pvi] * deviationRatio
                    S = at[3]
                    if S != max(values[pvi], S):
                        risk = laplace_DV_P2([-D, D], max(values[pvi]/epsilon, S/epsilon), S/epsilon)
                    else:
                        risk = laplace_DV_P([-D, D], S/epsilon)
                    risk = round(risk, 2)
                    if abs(risk - round(risk, 1)) <= 1e-3 and risk != 1 and int(risk * 10)  != 0:
                        temp[int(risk * 10) - 1] += 1
                    else:
                        if risk == 1:
                            temp[int(risk * 10) - 1] += 1
                        else:
                            temp[int(risk * 10)] += 1
                    if len(ARL) == 4 and int(risk*10) >= 2:
                        print('xxx')

            if AttackNum != 0:
                for i in range(10):
                    temp[i] /= AttackNum
            ARL.append(temp)
    # 求count的结果
    attackRisk = laplace_DV_P([0, 0.5], 1 / epsilon) + 0.5
    attackRiskIdx = int(attackRisk*10)
    if abs(attackRisk - round(attackRisk, 1)) <= 1e-3 and attackRisk != 1 and attackRiskIdx != 0:
        attackRiskIdx -= 1
    return {'sum': sumRet, 'count': [attackRisk, attackRisk,
                                     [1 if i == attackRiskIdx else 0 for i in range(10)]]}