import itertools
import json
import time
from collections import defaultdict

import numpy as np
import pandas as pd

from utils.func import laplace_DV_P

start = time.time()
# df = pd.read_csv('test_data/Customer Portraits.csv')
df = pd.read_csv('test_data/Medical Cost.csv')
# df.drop('ID', axis=1, inplace=True)
attrs = df.columns.tolist()
df.fillna(0, inplace=True)
rawValues = df.values
values = df.values

n = len(values)
sensitiveAttrIdx = attrs.index('charges')
# sensitiveAttrIdx = attrs.index('Income')

#1 Medical
#2 Customer
#3 Habit

highRiskNum = n // 5


print(df.columns.tolist())

attrProp = {}
for i, attr in enumerate(attrs):
    if type(values[0][i]) == str:
        scope = list(set(map(lambda d: d[i], values)))
        attrProp[attr] = {
            'scope': scope,
            'type': 'categorical',
            'map': dict(zip(scope, range(len(scope))))

        }
    else:
        maxx = max(values, key=lambda d: d[i])[i]
        minn = min(values, key=lambda d: d[i])[i]
        width = (maxx - minn) / 20
        attrProp[attr] = {
            'scope': [minn-width, maxx+width],
            'type': 'numerical',
            'width': width
        }

for i, attr in enumerate(attrs):
    prop = attrProp[attr]
    if prop['type'] == 'numerical':
        for j in range(n):
            values[j][i] = (values[j][i] - prop['scope'][0]) / prop['width']
    else:
        for j in range(n):
            values[j][i] = prop['map'][values[j][i]]


charges = list(map(lambda d: d[sensitiveAttrIdx], values))
charges.sort()
threshold1 = charges[-n//5]
specialKey = []

cntMap = defaultdict(list)
specialCntMap = defaultdict(list)
idxKeyMap = {}
# df.sort_values(by='charges', ascending=False).index
for i, d in enumerate(values):
    key = '-'.join(str(int(v)) for v in d.tolist())
    cntMap[key].append(i)
    specialKey = '-'.join(str(int(v)) for (idx, v) in enumerate(d.tolist()) if idx != sensitiveAttrIdx)
    specialCntMap[specialKey].append(i)
    idxKeyMap[i] = key

print(cntMap)
mapKeys = list(cntMap.keys())

specialCnt = 0
temp = []
specialIdx = []

for key, v in specialCntMap.items():
    if len(v) == 1:
        specialCnt += 1
        temp.append(v[0])

for si in temp:
    if values[si][sensitiveAttrIdx] > threshold1:
        specialIdx.append(si)


riskValues = values[specialIdx]
print(riskValues)
# sortedIdx = np.lexsort([-1*riskValues[:,sensitiveAttrIdx]])
# riskValueNum = len(sortedIdx)
# sortedRiskValues = riskValues[sortedIdx]

MaxS = 0
for si in range(n):
    MaxS = max(MaxS, rawValues[si][sensitiveAttrIdx])

attrNum = len(riskValues[0])
attrChars = [chr(ord('a') + i) for i in range(attrNum)]
attrChars.remove(chr(ord('a') + sensitiveAttrIdx))
attrSetIdxMap = defaultdict(list)
Attack = defaultdict(list)
epsilon = 1
dp = 0.4  #deviation percent
for an in range(1, len(attrChars)+1):
    attrSets = list(itertools.combinations(attrChars, an))
    for i in range(len(riskValues)):
        curKey = '-'.join(str(int(v)) for v in riskValues[i].tolist())
        curKeyA = curKey.split('-')

        for attrSet in attrSets:
            find = False
            findAttr = []
            attrIdxSet = [ord(j) - ord('a') for j in attrSet]
            findAttrName = [attrs[idx] for idx in attrIdxSet]
            for mk in mapKeys:
                if mk == curKey:
                    continue
                else:
                    mka = mk.split('-')
                    for ai in attrIdxSet:
                        if mka[ai] != curKeyA[ai]:
                            break
                    else:
                        find = True
                        break
            if not find:
                findAttr = attrSet
                attrSetIdxMap[findAttr].append(i)
                pvi = i
                D = rawValues[pvi][sensitiveAttrIdx] * dp
                risk = laplace_DV_P([-D, D], MaxS / epsilon)
                Attack[len(findAttr)].append([pvi, findAttrName, MaxS, risk])

for an in Attack.keys():
    Attack[an].sort(key=lambda d: -d[-1])
    Attack[an] = Attack[an][0:10]

ASIM = dict(attrSetIdxMap)
print(ASIM)
IASM = defaultdict(list)
for k, v in ASIM.items():
    for idx in v:
        curKeyList = IASM[idx]
        for ck in curKeyList:
            if len(k) > len(ck):
                same = True
                for i in range(len(ck)):
                    if ck[i] not in k:
                        same = False
                        break
                if same:
                    break
        else:
            IASM[idx].append([attrs[ord(c) - ord('a')] for c in k])

riskMap = {}


for i, si in enumerate(specialIdx):
    D = rawValues[si][sensitiveAttrIdx] * dp
    riskMap[i] = laplace_DV_P([-D, D], MaxS/epsilon)

print(riskMap)

attrs.remove(attrs[sensitiveAttrIdx])
data = {
    'attrs': attrs,
    'Attack': Attack
}

with open("data/data.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(data, indent=4))

end = time.time()
print("运行时间:", end-start, '秒')




# Pleak = [0.8, 1.0, 0.8, 0.8, 1.0, 1.0, 0.3]
#
# attrIndicesList = ['1', '4', '5', '1-4', '1-5', '4-5', '0-1-2-4-5']
#
#
# attrSetMap = dict()
# attrNum = 7
# for i in range(1, attrNum):
#     combs = itertools.combinations(range(7), i)
#     for comb in combs:
#         attrSetMap[comb] = Pleak[min(comb, key=lambda d: Pleak[d])]
#
# attrSetItems = list(attrSetMap.items())
# attrSetItems.sort(key=lambda d: -len(d[0]))
# attrSetItems.sort(key=lambda d: -d[1])
#
# temp = df['charges'][specialIdx]
# temp = temp.sort_values(ascending=False)
# sortedIdx = temp.index.tolist()
# top10Idx = sortedIdx[:10]
# print(top10Idx)
#
# print(specialCnt, len(values), specialCnt / len(values))
#
#
# testKey = list(map(lambda d: int(d), idxKeyMap[top10Idx[0]].split('-')))
# highRiskMap = {}
# for asi in attrSetItems:
#     attrIndices = asi[0]
#     find = 0
#     for key in cntMap.keys():
#         if key != idxKeyMap[top10Idx[0]]:
#             curKeyList = list(map(lambda d: int(d), key.split('-')))
#             for idx in attrIndices:
#                 if testKey[idx] != curKeyList[idx]:
#                     break
#             else:
#                 find = 1
#                 break
#     if find == 0:
#         highRiskMap[top10Idx[0]] = attrIndices
#         break
# print(highRiskMap)
