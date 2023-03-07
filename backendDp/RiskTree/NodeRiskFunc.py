<<<<<<< HEAD
=======
from collections import defaultdict

>>>>>>> ec03867 (initial)
from RiskTree.Class import DataCoder


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


def isOneNumLp(x, p):
    count = 0
    while x:
        x = x & (x - 1)
        count += 1
        if count > p:
            return True
    return False


def binaryInclusion(x, y):
    # y : target
    if x <= y:
        return False
    while y:
        if y & 1 == 1:
            if not x & 1:
                return False
        x = x >> 1
        y = y >> 1
    return True


def ConstructLattice(n, depth):
    cuboid = int('1' * n, 2)
    lattice = [i for i in range(1, cuboid + 1) if isWithinDepth(i, depth)]
    return lattice


def isWithinDepth(x, depth):
    indices = getCubeByIndices(x)
    return len(indices) <= depth


def getDataCoder(data, column_types, gap_list=None, step_list=None):
    gap, step = 1, 1
    columns = data.columns.tolist()
    DCs = []
    for (i, column) in enumerate(columns):
        # 首先得知道数据的范围
        if column_types[i] == 'numerical':
            Min = data.min()[column]
            params = {
                'Min': Min,
                'gap': gap,
                'step_ratio': 0.1
            }
            DC = DataCoder(column_types[i], params)
            DCs.append(DC)
        else:
            category_map = {}
            categories = set(data[column].tolist())
            for (index, category) in enumerate(categories):
                category_map[category] = index
            DC = DataCoder(column_types[i], category_map)
            DCs.append(DC)
    return DCs


def getCodedData(data, DCs):
    columns = data.columns.tolist()
    for i, column in enumerate(columns):
        # 跟用apply时间花费差不多
        data[column] = data[column].map(lambda x: DCs[i].enCoder(x))


def GenerateCandidateTupleIndex(q, n, childrenMap, BSTMap, RiskRatioMap):
    children = childrenMap.get(q, [])
    CandidateTuple = set(range(n))
    pruning_node = set()
    for child in children:
        pruning_node = BSTMap[child] | pruning_node
    CandidateTuple -= pruning_node
    RiskRatioMap[str(q)] = [len(pruning_node), 0]
    return CandidateTuple


def getNodeRisk(values):
    # values 是编码后的表格
    m, n = len(values[0]), len(values)
    lattice = ConstructLattice(m, 3)
    BSTMap = {}
<<<<<<< HEAD
=======
    BSTKeyMap = defaultdict(list)
>>>>>>> ec03867 (initial)
    riskRecord = set()
    RiskRatioMap = {}
    # 创建节点相关关系,比如AB的字节点是A 和 B,可以对A和B的BST剪枝
    childrenMap = getChildrenMap(lattice)
    for q in lattice:
        GroupMap = {}
        indices = getCubeByIndices(q)
        candidateTuple = GenerateCandidateTupleIndex(q, n, childrenMap, BSTMap, RiskRatioMap)

        for i in candidateTuple:
            key = ''
            for j in indices:
                key += '-' + str(values[i][j])
<<<<<<< HEAD
                GroupMap[key] = GroupMap.get(key, [])
                GroupMap[key].append(i)
=======
            GroupMap[key] = GroupMap.get(key, [])
            GroupMap[key].append(i)
>>>>>>> ec03867 (initial)

        BSTMap[q] = set()
        for key in GroupMap.keys():
            if len(GroupMap[key]) == 1:
                index = GroupMap[key][0]
                BSTMap[q].add(index)
                riskRecord.add(index)
<<<<<<< HEAD
        RiskRatioMap[str(q)][0] += len(BSTMap[q])
        RiskRatioMap[str(q)][1] += len(GroupMap) - len(BSTMap[q])

    return BSTMap, RiskRatioMap, riskRecord
=======

                keys = key.split('-')
                keys.pop(0)
                if len(indices) != len(keys):
                    print('AAA')
                BSTKeyMap[index].append({
                    'indices': indices,
                    'keys': keys
                })

        RiskRatioMap[str(q)][0] += len(BSTMap[q])
        RiskRatioMap[str(q)][1] += len(GroupMap) - len(BSTMap[q])

    return BSTMap, BSTKeyMap, RiskRatioMap, riskRecord
>>>>>>> ec03867 (initial)


def getChildNodeRiskRatio(bitmaps, RiskRatioMap, m):
    ChildNodeRiskRatio = {}
    lattice = ConstructLattice(m, 3)
    for target in bitmaps:
        ChildNodeRiskRatio[target] = [0, 0]
        for q in lattice:
            if len(getCubeByIndices(q)) == 3 and binaryInclusion(q, target):
                ChildNodeRiskRatio[target][0] += RiskRatioMap[str(q)][0]
                ChildNodeRiskRatio[target][1] += RiskRatioMap[str(q)][1]
    return ChildNodeRiskRatio

