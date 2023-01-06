# 接收文件，返回数据
import itertools
import time

import pandas as pd

from RiskTree.Class import DataCoder

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


def GenerateCandidateTupleIndex(q, n, childrenMap, BSTMap):
    children = childrenMap.get(q, [])
    CandidateTuple = set(range(n))

    # 先不剪枝
    # for child in children:
    #     CandidateTuple -= BSTMap[child]
    return CandidateTuple


def getCodedData(data, DCs):
    columns = data.columns.tolist()
    for i, column in enumerate(columns):
        data[column] = data[column].map(lambda x: DCs[i].enCoder(x))


def BFS(values, lattice, n, childrenMap):
    BSTMap = {}
    for q in lattice:
        GroupMap = {}
        indices = getCubeByIndices(q)
        candidateTuple = GenerateCandidateTupleIndex(q, n, childrenMap, BSTMap)
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


def makeTree(BSTMap, n, m, bitmap):
    # print(BSTMap)
    ret = []
    indices = getCubeByIndices(bitmap)
    dimensions = [i for i in range(m) if i not in indices]
    for dimension in dimensions:
        new_bitmap = bitmap + (1 << dimension)
        bst_count = len(BSTMap[new_bitmap])
        ret.append({
                'name': new_bitmap,
                'pie': [bst_count, n - bst_count],
                'children': [],
                'val': 1
            })
    return ret


def getRiskRecord(filename, attrList, bitmap):
    R = pd.read_csv('data/{0}'.format(filename))
    keepAttr = map(lambda d: d['Name'], attrList)
    BSTMap = {}
    rBSTMap = {}
    R = R[keepAttr]
    # R.drop(columns=dropColumns, inplace=True)
    R.fillna(0, inplace=True)
    n = R.shape[0]
    m = R.shape[1]
    Indices = getCubeByIndices(bitmap)
    column_types = list(map(lambda d: d['Type'], attrList))
    cur_column_types = [column_types[i] for i in Indices]
    start_time = time.time()
    DCs = getDataCoder(R, attrList)
    getCodedData(R, DCs)
    values = R.values
    lattice = ConstructLattice(bitmap, m)
    childrenMap = getChildrenMap(lattice)
    BSTMap = BFS(values, lattice, n, childrenMap)
    tree = {
        'name': bitmap,
        'pie': [0, n],
        'children': makeTree(BSTMap, n, m, bitmap)
    }
    end_time = time.time()
    run_time = end_time - start_time
    json_data = {
        'treeData': tree,
        'run_time': run_time,
        'Indices': Indices
    }
    return json_data

