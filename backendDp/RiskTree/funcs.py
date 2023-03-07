# 接收文件，返回数据
import itertools
import math
import time
<<<<<<< HEAD
from functools import reduce

=======
from collections import defaultdict
from functools import reduce

import numpy as np
>>>>>>> ec03867 (initial)
import pandas as pd

from RiskTree.Class import DataCoder
from RiskTree.NodeRiskFunc import getNodeRisk, getChildNodeRiskRatio
<<<<<<< HEAD
from tools.utils import laplace_DV_P
=======
from tools.df_processor import DFProcessor
from tools.utils import laplace_DV_P, laplace_DV_P2
>>>>>>> ec03867 (initial)


def key2string(key, DataCoder):
    type = DataCoder.type
    params = DataCoder.params
    if type == 'numerical':
        Min, Width = params['Min'], params['Width']
        ret = "{0}~{1}".format(Min + Width * key, Min + Width * key + Width)
    else:
        ret = params['rmap'][key]
    return ret


<<<<<<< HEAD

=======
>>>>>>> ec03867 (initial)
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
            Width = attrList[i]['DAable Window Width']
            MaxEdge = attrList[i]['Search Max Edge']
            MinEdge = attrList[i]['Search Min Edge']
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
            categories = set(data[column].tolist())
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
<<<<<<< HEAD
           indices.append(i)
=======
            indices.append(i)
>>>>>>> ec03867 (initial)
        i += 1
        x = x >> 1
    return indices


def GenerateCandidateTupleIndex(n):
    # 本来是用来剪枝的,但是交互模式更改后就不需要剪枝了
    CandidateTuple = range(n)
    return CandidateTuple


def getCodedData(data, DCs):
    columns = data.columns.tolist()
    for i, column in enumerate(columns):
        data[column] = data[column].map(lambda x: DCs[i].enCoder(x))


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
<<<<<<< HEAD
                'indices': indices + [dimension],
                'name': new_bitmap,
                'childNodeRiskPie': childNodeRiskRatio[new_bitmap],
                'curNodeRiskPie': RiskRatioMap[str(new_bitmap)],
                'children': [],
                'val': 1
            })
=======
            'indices': indices + [dimension],
            'name': new_bitmap,
            'childNodeRiskPie': childNodeRiskRatio[new_bitmap],
            'curNodeRiskPie': RiskRatioMap[str(new_bitmap)],
            'children': [],
            'val': 1
        })
>>>>>>> ec03867 (initial)
    return ret


def indices2bitmap(indices):
    ret = 0
    for index in indices:
        ret += 1 << index
    return ret


def getRiskRecord(filename, attrList, indices, RiskRatioMap):
    R = pd.read_csv('data/{0}'.format(filename))
    keepAttr = map(lambda d: d['Name'], attrList)
    BSTMap = {}
<<<<<<< HEAD
=======
    BSTKeyMap = defaultdict(list)
>>>>>>> ec03867 (initial)
    R = R[keepAttr]
    R.fillna(0, inplace=True)
    n = R.shape[0]
    m = R.shape[1]
    bitmap = indices2bitmap(indices)
    start_time = time.time()
    DCs = getDataCoder(R, attrList)
    getCodedData(R, DCs)
    values = R.values
    lattice = ConstructLattice(bitmap, m)
    riskRecord = set()
    if RiskRatioMap == -1:
<<<<<<< HEAD
        BSTMap, RiskRatioMap, riskRecord = getNodeRisk(values) #遍历了全部记录
    riskRecord = list(riskRecord)
    childNodeRiskRatio = getChildNodeRiskRatio(lattice, RiskRatioMap, m)
    print(RiskRatioMap, '\n',childNodeRiskRatio)
=======
        BSTMap, BSTKeyMap, RiskRatioMap, riskRecord = getNodeRisk(values)  # 遍历了全部记录
    riskRecord = list(riskRecord)
    childNodeRiskRatio = getChildNodeRiskRatio(lattice, RiskRatioMap, m)
    print(RiskRatioMap, '\n', childNodeRiskRatio)
>>>>>>> ec03867 (initial)
    tree = {
        'indices': indices,
        'name': bitmap,
        'childNodeRiskPie': [0, 0],
        'curNodeRiskPie': [0, n],
        'children': makeTree(indices, m, bitmap, RiskRatioMap, childNodeRiskRatio)
    }
    end_time = time.time()
    run_time = end_time - start_time

    # BST内的set转list
    for key in BSTMap.keys():
        BSTMap[key] = list(BSTMap[key])

    json_data = {
        'treeData': tree,
        'run_time': run_time,
        'Indices': indices,
        'RiskRatioMap': RiskRatioMap,
        'BSTMap': BSTMap,
<<<<<<< HEAD
=======
        'BSTKeyMap': BSTKeyMap,
>>>>>>> ec03867 (initial)
        'riskRecord': riskRecord
    }
    return json_data

<<<<<<< HEAD
def getAvgRiskP(filename, attr, deviationRatio, attrParams, epsilon, riskRecord, type, sensitivity):
    R = pd.read_csv('data/{0}'.format(filename))
    R.fillna(0, inplace=True)
    R = R[attr]
    b = sensitivity / epsilon
    barData = {}
    # count类型时, 数值型和类别型一致
    if type == 'count':
        deviation = '-'


    if attrParams['Type'] != 'numerical': #类别型数据
        return laplace_DV_P([0, 0.5], b) + 0.5
    else: #数值型数据
        for i in range(10):
            barData[i] = 0
        for index in riskRecord:
            deviation = R[index] * deviationRatio
            p = laplace_DV_P([-deviation, deviation], b)
            key = math.floor(p * 100) // 10
            barData[key] += 1
        return barData


=======

def keys2condition(AttrsKeyMap, dc_indices, dc_keys):
    conditions = {}
    otherConditions = {}
    for dc_index, dc_key in zip(dc_indices, dc_keys):
        keyMap = AttrsKeyMap[dc_index]
        keys, texts, type = keyMap['data'], keyMap['text'], keyMap['type']
        dc_text = texts[keys.index(int(float(dc_key)))]
        if type == 'numerical':
            conditions[dc_index] = list(map(lambda d: float(d), dc_text.split('~')))
            otherConditions[dc_index] = [list(map(lambda d: float(d), text.split('~'))) for text in texts if text != dc_text]
        else:
            conditions[dc_index] = dc_text
            otherConditions[dc_index] = [text for text in texts if text != dc_text]
    return conditions, otherConditions


def getMinLocalSensitivityMap(AttrsKeyMap, BSTKeyMap, attrOption, filename, attr):
    minSensitivityMap = {}
    for bstIndex in BSTKeyMap.keys():
        minSensitivity = float('inf')
        # differencing condition
        for dc in BSTKeyMap[bstIndex]:
            dc_indices = dc['indices']
            dc_keys = dc['keys']
            dcConditions, otherConditions = keys2condition(AttrsKeyMap, dc_indices, dc_keys)

            # 选择差分属性的other条件任意组合(时间复杂度极高
            # attrs = [attrOption[index] for index in dc_indices]
            # QueryCondition = {}
            # for conditions in itertools.product(*otherConditions.values()):
            #     for conditionAttr, condition in zip(attrs, conditions):
            #         QueryCondition[conditionAttr] = [condition]
            #     dfp = DFProcessor(filename, attr, QueryCondition, 'Local sensitivity')
            #     sensitivity = dfp.getCurSensitivity('sum')
            #     if sensitivity == 'None':
            #         continue
            #     else:
            #         minSensitivity = min(minSensitivity, sensitivity)

            # 选定不同的属性作为差分条件时
            for dc_index, dc_key in zip(dc_indices, dc_keys):
                normalCondition = [dcConditions[index] for index in dc_indices if index != dc_index]
                normalAttr = [attrOption[index] for index in dc_indices if index != dc_index]
                dcCondition = otherConditions[dc_index]
                dcAttr = attrOption[dc_index]
                for dc in dcCondition:
                    QueryCondition = {dcAttr: [dc]}
                    for n_attr, condition in zip(normalAttr, normalCondition):
                        QueryCondition[n_attr] = [condition]
                    dfp = DFProcessor(filename, attr,
                                      QueryCondition, 'Local sensitivity')
                    sensitivity = dfp.getCurSensitivity('sum')
                    if sensitivity == 'None':
                        continue
                    else:
                        minSensitivity = min(minSensitivity, sensitivity)
        minSensitivityMap[int(bstIndex)] = minSensitivity
    return minSensitivityMap


# def getMinLocalSensitivity(attrR):
#     s = attrR.nsmallest(2)
#     return float(s.values[1])


def getAvgRiskP(filename, attr, attrParams, epsilon, attrOption, sensitivity, attrRisk, BSTMap, SensitivityCalculationWay, AttrsKeyMap, BSTKeyMap):
    R = pd.read_csv('data/{0}'.format(filename))
    R.fillna(0, inplace=True)
    attrR = R[attr]
    attrIndex = attrOption.index(attr)
    barData = {}
    minSensitivityMap = {}
    # query2S = 0
    if SensitivityCalculationWay == 'Local sensitivity':
        minSensitivityMap = getMinLocalSensitivityMap(AttrsKeyMap, BSTKeyMap, attrOption, filename, attr)

    if attrParams['Type'] != 'numerical':  # 类别型数据
        attackRisk = laplace_DV_P([0, 0.5], sensitivity['count'] / epsilon) + 0.5
        sumRisk = 0
        cnt = 0
        for bitmap in BSTMap:
            indices = getCubeByIndices(int(bitmap))
            if attrIndex in indices:
                continue
            for index in BSTMap[bitmap]:
                minAttrRiskP = 1
                if attrRisk.get(str(bitmap), -1) != -1:
                    minAttrRiskP = attrRisk[str(bitmap)]
                else:
                    for attrIndex in indices:
                        minAttrRiskP = min(minAttrRiskP, attrRisk[str(attrIndex)])
                sumRisk += minAttrRiskP * attackRisk
                cnt += 1
        return {'sum': '-', 'count': [attackRisk, sumRisk / cnt]}
    else:  # 数值型数据
        sumRet = {'avgRiskList': [], 'attackRiskList': []}
        for deviationRatio in np.linspace(0, 1, 11):
            pMap = defaultdict(int)
            attackPMap = defaultdict(int)
            riskNum = 0
            for i in range(10):
                barData[i] = 0
            for bitmap in BSTMap:
                indices = getCubeByIndices(int(bitmap))
                if attrIndex in indices:
                    continue
                for index in BSTMap[bitmap]:
                    minAttrRiskP = 1
                    if attrRisk.get(str(bitmap), -1) != -1:
                        minAttrRiskP = attrRisk[str(bitmap)]
                    else:
                        for attrIndex in indices:
                            minAttrRiskP = min(minAttrRiskP, attrRisk[str(attrIndex)])
                    # deviation = sensitivity['sum'] * deviationRatio
                    deviation = attrR[index] * deviationRatio
                    if SensitivityCalculationWay == 'Local sensitivity':
                        query1S = max(minSensitivityMap[index], attrR[index])
                        query2S = minSensitivityMap[index]
                        if query1S == query2S:
                            p = laplace_DV_P([-deviation, deviation], query1S / epsilon)
                        else:
                            p = laplace_DV_P2([-deviation, deviation], query1S / epsilon, query2S / epsilon)
                    else:
                        p = laplace_DV_P([-deviation, deviation], sensitivity['sum'] / epsilon)
                    pMap[index] = max(pMap[index], p * minAttrRiskP)
                    attackPMap[index] = max(pMap[index], p * minAttrRiskP)
            for p in attackPMap.values():
                key = min(math.floor(p * 100) // 10, 9)
                barData[key] += 1
                riskNum += 1
            sumRet['avgRiskList'].append(math.fsum(pMap.values()) / len(pMap))
            sumRet['attackRiskList'].append(list(map(lambda d: d/riskNum, barData.values())))

        # 求count的结果
        attackRisk = laplace_DV_P([0, 0.5], sensitivity['count'] / epsilon) + 0.5
        sumRisk = 0
        cnt = 0
        for bitmap in BSTMap:
            indices = getCubeByIndices(int(bitmap))
            if attrIndex in indices:
                continue
            for index in BSTMap[bitmap]:
                minAttrRiskP = 1
                if attrRisk.get(str(bitmap), -1) != -1:
                    minAttrRiskP = attrRisk[str(bitmap)]
                else:
                    for attrIndex in indices:
                        minAttrRiskP = min(minAttrRiskP, attrRisk[str(attrIndex)])
                sumRisk += minAttrRiskP * attackRisk
                cnt += 1
        return {'sum': sumRet, 'count': [attackRisk, sumRisk / cnt]}
>>>>>>> ec03867 (initial)
