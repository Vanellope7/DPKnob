import math

from RiskTree.Class import DataCoder

def getMaxEdge(width, MinEdge, Max):
    r = math.ceil((Max - MinEdge) / width)
    if MinEdge + r * width <= Max:
        r += 1
    return MinEdge + r * width

def getMinEdge(width, Min):
    MinEdge = Min - (Min % width)
    return MinEdge


def getGap(left, right):
    if right - left < 10:
        return 1, 5
    gap = float((right - left) / 20)
    gap_str = str(gap).split('.')
    if gap > 1:
        if gap >= 5 and gap < 10:
            return gap // 5 * 5, 5
        else:
            bit = len(gap_str[0]) - 1
            return 10 ** bit, bit
    else:
        bit = len(gap_str[1]) - 1
        if bit == 0:
            return 1, 0
        return round(gap, bit), bit



def binaryInclusion(x, y):
    while x and y:
        if x & 1 != y & 1:
            return False
        else:
            x = x >> 1
            y = y >> 1
    return True


def getCodedData(data, DCs):
    columns = data.columns.tolist()
    for i, column in enumerate(columns):
        data[column] = data[column].map(lambda x: DCs[i].enCoder(x))


def DFS_OUTER(input, d, bitmap, depth, dim, R):
    global values
    values = R
    return DFS(input, d, bitmap, depth, dim, True)


def DFS(input, d, bitmap, depth, dim, show=True):
    ret = []
    if depth > dim - 1:
        return []
    global values

    GroupMap = {}  # key: valueKey   value: index
    for i in input:
        key = values[i][d]
        GroupMap[key] = GroupMap.get(key, [])
        GroupMap[key].append(i)

    for key in sorted(GroupMap.keys()):
        # 统计BST比率
        subgroup = GroupMap[key]
        subgroup_size = len(subgroup)
        if subgroup_size == 1:
            # 记录BST，并且对expand BST进行去重
            BST = subgroup[0]
            ret.append({
                'dim': d,
                'key': key,
                'val': 1 if depth == dim - 1 else 0,
                'isBST': True,
                'index': [BST],
                'show': show,
                'num': subgroup_size,
                'children': DFS(GroupMap[key], d + 1, bitmap + (1 << d), depth + 1, dim, False)
            })

        else:
            ret.append({
                'dim': d,
                'val': 0,
                'key': key,
                'isBST': False,
                'index': subgroup,
                'show': show,
                'num': subgroup_size,
                'children': DFS(GroupMap[key], d + 1, bitmap + (1 << d), depth + 1, dim)
            })

    return ret

def sortColumn(data):
    new_column = data.var(numeric_only=True).sort_values(ascending=False).index.tolist()
    return new_column