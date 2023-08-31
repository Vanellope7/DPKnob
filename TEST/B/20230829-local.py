import itertools
import json
import time
from collections import defaultdict

# import fim
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils.func import laplace_DV_P, laplace_DV_P2, listIncluded

# df = pd.read_csv('test_data/Customer Portraits.csv')
df = pd.read_csv('test_data/Medical Cost.csv')
# df.drop('ID', axis=1, inplace=True)
attrs = df.columns.tolist()
attrNum = len(attrs)
df.fillna(0, inplace=True)
rawValues = df.values
values = df.values
n = len(rawValues)

# sensitiveAttr = 'Income'
sensitiveAttr = 'charges'
sensitiveAttrIdx = attrs.index(sensitiveAttr)
charges = df[sensitiveAttr].sort_values()

threshold = charges[n//5]

start = time.time()

attrProp = {}
for i, attr in enumerate(attrs):
    if type(values[0][i]) == str:
        scope = list(set(map(lambda d: d[i], values)))
        scope.sort()
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
end = time.time()
# print(end-start)
for i, attr in enumerate(attrs):
    if attr == sensitiveAttr:
        for j in range(n):
            values[j][i] = values[j][i] <= threshold
    else:
        prop = attrProp[attr]
        if prop['type'] == 'numerical':
            for j in range(n):
                values[j][i] = (values[j][i] - prop['scope'][0]) / prop['width']
        else:
            for j in range(n):
                values[j][i] = prop['map'][values[j][i]]

end = time.time()
# print(end-start)

tracts = []
for v in values:
    md = []
    for i, d in enumerate(v):
        md.append(chr(ord('a') + i) + str(int(d)))
    tracts.append(md)




    # for t in tracts:
    #     if 'd5' in t and 'f3' in t and 'b1' in t and 'e0' in t:
    #         print(t)



cntMap = defaultdict(list)
specialCntMap = defaultdict(list)
idxKeyMap = {}
for i, d in enumerate(values):
    key = '-'.join(str(int(v)) for v in d.tolist())
    cntMap[key].append(i)
    specialKey = '-'.join(str(int(v)) for (idx, v) in enumerate(d.tolist()) if idx != sensitiveAttrIdx)
    specialCntMap[specialKey].append(i)
    idxKeyMap[i] = key



specialCnt = 0
specialIdx = []
victimKey = []
for key, v in specialCntMap.items():
    if len(v) == 1:
        specialCnt += 1
        specialIdx.append(v[0])
        victimKey.append(idxKeyMap[v[0]])




attrChars = [chr(ord('a') + i) for i in range(attrNum)]
attrChars.remove(chr(ord('a') + sensitiveAttrIdx))
allCombination = []
for an in range(1, len(attrChars)+1):
    attrSets = list(itertools.combinations(attrChars, an))
    allCombination.extend(attrSets)
mapKeys = cntMap.keys()
mapKeys = list(map(lambda d: d.split('-'), mapKeys))

kMapKey = list(filter(lambda d: d[sensitiveAttrIdx] == '1', mapKeys))
nkMapKey = list(filter(lambda d: d[sensitiveAttrIdx] == '0', mapKeys))
start_time = time.time()
specialCon = {}
for attrSet in allCombination:
    attrIdx = tuple(map(lambda d: ord(d) - ord('a'), attrSet))
    attrV1 = set(['-'.join(map(lambda i: k[i], attrIdx)) for k in kMapKey])
    attrV2 = set(['-'.join(map(lambda i: k[i], attrIdx)) for k in nkMapKey])
    attrV = list(attrV1 - attrV2)
    if len(attrV) > 0:
        specialCon[attrIdx] = attrV
end_time = time.time()
print('算法运行时间', end_time - start_time)
# print(specialCon)

minSensitivity = defaultdict(dict)
attrSetIdxMap = defaultdict(list)

t1 = 0
t2 = 0
t3 = 0
t4 = 0

Quadruple = defaultdict(list)
candidateRecord = {}
for attrIdx in specialCon.keys():
    for key in specialCon[attrIdx]:
        keyL = key.split('-')
        for differAttr in attrIdx:
            for differVal in [1, -1]:
                candidate = mapKeys
                s1 = time.time()
                curCon = []
                for i, attr in enumerate(attrIdx):
                    if attr == differAttr:
                        curCon.append((i, int(keyL[i]) + differVal))
                        if candidateRecord.get(tuple(curCon), 0) == 0:
                            candidate = list(filter(lambda d: int(d[attr]) == int(keyL[i])+differVal, candidate))
                            candidateRecord[tuple(curCon)] = candidate
                        else:
                            candidate = candidateRecord.get(tuple(curCon))

                    else:
                        curCon.append((i, int(keyL[i])))
                        if candidateRecord.get(tuple(curCon), 0) == 0:
                            candidate = list(filter(lambda d: d[attr] == keyL[i], candidate))
                            candidateRecord[tuple(curCon)] = candidate
                        else:
                            candidate = candidateRecord.get(tuple(curCon))
                e1 = time.time()
                t1 += e1 - s1
                if len(candidate) == 1:
                    s2 = time.time()
                    idxL = cntMap['-'.join(candidate[0])]
                    if len(idxL) == 1:
                        pvi = idxL[0]
                        findAttr = list(map(lambda d: attrs[d], attrIdx))
                        attrSetIdxMap[tuple(findAttr)].append(pvi)

                        # 更新局部敏感度
                        secondQueryGroup = mapKeys
                        curCon = []
                        for i, attr in enumerate(attrIdx):
                            curCon.append((i, int(keyL[i])))
                            if candidateRecord.get(tuple(curCon), 0) == 0:
                                secondQueryGroup = list(filter(lambda d: d[attr] == keyL[i], secondQueryGroup))
                                candidateRecord[tuple(curCon)] = secondQueryGroup
                            else:
                                secondQueryGroup = candidateRecord.get(tuple(curCon))
                        MaxS = 0
                        for secondK in secondQueryGroup:
                            S = rawValues[max(cntMap['-'.join(secondK)], key=lambda d: rawValues[d][sensitiveAttrIdx])][
                                sensitiveAttrIdx]
                            MaxS = max(S, MaxS)
                        nx = len(attrIdx)
                        minSensitivity[pvi][nx] = minSensitivity[pvi].get(nx, MaxS)
                        minSensitivity[pvi][nx] = min(MaxS, minSensitivity[pvi][nx])
                        if len(list(filter(lambda d: d[0] == pvi, Quadruple[nx]))) == 0:
                            Quadruple[nx].append([pvi, findAttr, minSensitivity[pvi][nx]])
                    e2 = time.time()
                    t2 += e2 - s2
print(Quadruple)
print('t1: ', t1)
print('t2: ', t2)
end = time.time()
print('运行时间:', end-start)
for k in attrSetIdxMap.keys():
    attrSetIdxMap[k] = list(set(attrSetIdxMap[k]))
# print(attrSetIdxMap)

ASIM = dict(attrSetIdxMap)
IASM = defaultdict(list)

for k, v in ASIM.items():
    for idx in v:
        IASM[idx].append(k)

MinLen = attrNum
MaxLen = -1
for idx in IASM.keys():
    IASM[idx].sort(key=lambda d: len(d))
    filterIdx = []
    for i, attrS in enumerate(IASM[idx]):
        for j in range(0, i):
            if listIncluded(attrS, IASM[idx][j]):
                filterIdx.append(i)
                break
    IASM[idx] = [v for ii, v in enumerate(IASM[idx]) if ii not in filterIdx]


riskMap = defaultdict(dict)
epsilon = 1
dp = 0.4  #deviation percent

NumRiskMap = defaultdict(list)
for i in IASM.keys():
    for an in minSensitivity[i].keys():
        S1 = max(minSensitivity[i][an], rawValues[i][sensitiveAttrIdx])
        S2 = minSensitivity[i][an]
        if S2 == 0:
            S2 += 0.1
        D = rawValues[i][sensitiveAttrIdx] * dp
        risk = laplace_DV_P2([-D, D], S1/epsilon, S2/epsilon)
        riskMap[i][an] = risk
        NumRiskMap[an].append(risk)
for key in NumRiskMap.keys():
    NumRiskMap[key].sort(key= lambda d: -d)





for nx, ats in Quadruple.items():
    for i in range(len(ats)):
        pvi = ats[i][0]
        riskV = rawValues[pvi][sensitiveAttrIdx]
        S1 = max(ats[i][2], riskV)
        S2 = ats[i][2]
        if S2 == 0:
            S2 += 0.1
        D = riskV * dp
        risk = laplace_DV_P2([-D, D], S1/epsilon, S2/epsilon)
        ats[i].append(risk)
    Quadruple[nx].sort(key=lambda d: -d[-1])
print(Quadruple)

charges = list(charges)
left, right = charges[0], charges[-1]
maxRisk = laplace_DV_P2([-right*dp, right*dp], max(right/epsilon, threshold/epsilon), threshold/epsilon)
notContentNumL = []


for nx, ats in Quadruple.items():
    if len(ats) < 10:
        print('number: ', nx, 'smaller than 10')
        notContentNumL.append(nx)
    else:
        if ats[9][-1] >= maxRisk:
            print('number: ', nx, 'is content')
            pass
        else:
            print('number: ', nx, 'is not content')
            notContentNumL.append(nx)


test = defaultdict(list)
victimList = defaultdict(list)
for an in notContentNumL:
    attrSets = list(itertools.combinations(attrChars, an))
    for curKey in victimKey:
        curKeyA = curKey.split('-')
        keyL = curKeyA

        for attrSet in attrSets:
            find = False
            findAttr = []
            attrIdxSet = [ord(j) - ord('a') for j in attrSet]
            for mkl in mapKeys:
                mk = '-'.join(mkl)
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
                pvi = cntMap[curKey][0]
                findAttr = attrSet
                findAttrName = [attrs[j] for j in attrIdxSet]
                test[findAttr].append(pvi)

                # 更新风险

                attrIdx = attrIdxSet
                for differAttr in attrIdx:
                    for differVal in [1, -1]:
                        secondQueryGroup = mapKeys
                        for i, attr in enumerate(attrIdx):
                            curCon = []
                            if attr == differAttr:
                                curCon.append((i, int(keyL[i])+differVal))
                                if candidateRecord.get(tuple(curCon), 0) == 0:
                                    secondQueryGroup = list(filter(lambda d: int(d[attr]) == int(keyL[i])+differVal, secondQueryGroup))
                                    candidateRecord[tuple(curCon)] = secondQueryGroup
                                else:
                                    secondQueryGroup = candidateRecord.get(tuple(curCon))
                            else:
                                curCon.append((i, int(keyL[i])))
                                if candidateRecord.get(tuple(curCon), 0) == 0:
                                    secondQueryGroup = list(filter(lambda d: d[attr] == keyL[i], secondQueryGroup))
                                    candidateRecord[tuple(curCon)] = secondQueryGroup
                                else:
                                    secondQueryGroup = candidateRecord.get(tuple(curCon))
                        MaxS = 0
                        for secondK in secondQueryGroup:
                            S = rawValues[max(cntMap['-'.join(secondK)], key=lambda d: rawValues[d][sensitiveAttrIdx])][
                                sensitiveAttrIdx]
                            MaxS = max(S, MaxS)
                        victimList[an].append(pvi)
                        if MaxS >= threshold:
                            curV = rawValues[pvi][sensitiveAttrIdx]
                            risk = laplace_DV_P2([-curV*dp, curV*dp], max(curV/epsilon, MaxS/epsilon), MaxS/epsilon)
                            NumRiskMap[an].append(risk)

                            filterAttack = list(filter(lambda d: d[0] == pvi, Quadruple[an]))
                            if len(filterAttack) == 0:
                                Quadruple[an].append([pvi, findAttrName, MaxS, risk])
                            else:
                                filterAttack[0][-1] = max(filterAttack[0][-1], risk)
                                filterAttack[0][-2] = min(filterAttack[0][-2], MaxS)

    Quadruple[an].sort(key=lambda d: -d[-1])

    # print(NumRiskMap[an])
    NumRiskMap[an].sort(key=lambda d: -d)
    # print(NumRiskMap[an])

for an in Quadruple.keys():
    Quadruple[an] = Quadruple[an][0:10]
attrs.remove(attrs[sensitiveAttrIdx])
data = {
    'attrs': attrs,
    'Quadruple': Quadruple,
}
with open("data/Ldata.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(data, indent=4))

end = time.time()
print('总运行时间:', end-start)