# 接收文件，返回数据
import itertools
import time
from functools import reduce

import pandas as pd

from RiskTree.Class import DataCoder
from RiskTree.NodeRiskFunc import getNodeRisk, getNodeRiskRatio
from tools.utils import laplace_DV_P


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
           indices.append(i)
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
    return BSTMap


def makeTree(indices, BSTMap, n, m, bitmap, NodeRiskRatio):
    # print(BSTMap)
    ret = []
    dimensions = [i for i in range(m) if i not in indices]
    for dimension in dimensions:
        new_bitmap = bitmap + (1 << dimension)
        ret.append({
                'indices': indices + [dimension],
                'name': new_bitmap,
                'childNodeRiskPie': NodeRiskRatio[new_bitmap],
                'curNodeRiskPie': [len(BSTMap[new_bitmap]), n - len(BSTMap[new_bitmap])],
                'children': [],
                'val': 1
            })
    return ret


def indices2bitmap(indices):
    ret = 0
    for index in indices:
        ret += 1 << index
    return ret


def getRiskRecord(filename, attrList, indices, RiskMap):
    R = pd.read_csv('data/{0}'.format(filename))
    keepAttr = map(lambda d: d['Name'], attrList)
    BSTMap = {}
    rBSTMap = {}
    R = R[keepAttr]
    # R.drop(columns=dropColumns, inplace=True)
    R.fillna(0, inplace=True)
    n = R.shape[0]
    m = R.shape[1]
    bitmap = indices2bitmap(indices)
    start_time = time.time()
    DCs = getDataCoder(R, attrList)
    getCodedData(R, DCs)
    values = R.values
    lattice = ConstructLattice(bitmap, m)
    if RiskMap == -1:
        BSTMap, RiskMap = getNodeRisk(values) #遍历了全部记录
    else:
        BSTMap = BFS(values, lattice, n)

    NodeRiskRatio = getNodeRiskRatio(lattice, RiskMap, m)
    tree = {
        'indices': indices,
        'name': bitmap,
        'childNodeRiskPie': [0, 0],
        'curNodeRiskPie': [0, n],
        'children': makeTree(indices, BSTMap, n, m, bitmap, NodeRiskRatio)
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
        'RiskMap': RiskMap,
        'BSTMap': BSTMap
    }
    return json_data

def getAvgRiskP(filename, attr, deviation, attrParams, epsilon, BSTMap, type, sensitivity):
    R = pd.read_csv('data/{0}'.format(filename))
    R = R[attr]
    attrExposureP = list(map(lambda d: float(d['Exposure Probability']), attrParams))
    b = sensitivity / epsilon
    # count类型时, 数值型和类别型一致
    if type == 'count':
        deviation = '-'

    if deviation == '-': #类别型数据
        riskPSum = 0
        riskSum = 0
        for bitmap in BSTMap.keys():
            bitmap = int(bitmap)
            indices = getCubeByIndices(bitmap)
            exposeP = 1
            for index in indices:
                exposeP *= attrExposureP[index]
            riskP = exposeP * (laplace_DV_P([-0.5, 0], b) + 0.5)
            riskPSum += riskP * len(BSTMap[bitmap])
            riskSum += len(BSTMap[bitmap])
        return riskPSum / riskSum
    else: #数值型数据
        deviation = float(deviation)
        riskPSum = 0
        riskSum = 0
        for bitmap in BSTMap.keys():
            curRiskSum = len(BSTMap[bitmap])
            if curRiskSum == 0:
                continue
            bitmap = int(bitmap)
            indices = getCubeByIndices(bitmap)
            exposeP = 1
            for index in indices:
                exposeP *= attrExposureP[index]
            riskP = exposeP * laplace_DV_P([-deviation, deviation], b)
            riskPSum += riskP * curRiskSum
            riskSum += curRiskSum
        return riskPSum / riskSum


