import itertools
import json
import time
from collections import defaultdict

import fim
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

threshold = charges[n//2]

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

start_time = time.time()
r = fim.fpgrowth(tracts, zmin=2, supp=2, conf=100, target='r')
end_time = time.time()
# print('运行时间: ', end_time-start_time)
# print(r)

highRiskCon = []
num = 0
for t in r:
    if t[0] == chr(ord('a') + sensitiveAttrIdx) + '1':
        highRiskCon.append(t[1])
        num += 1
print('condition num:', num)

r = fim.fpgrowth(tracts, zmin=2, supp=2, conf=0, target='r')
for t in r:
    if t[0] == chr(ord('a') + sensitiveAttrIdx) + '0':
        highRiskCon.append(t[1])
        num += 1
print('condition num:', num)
print(len(set(highRiskCon)), len(highRiskCon))

mapKeys = cntMap.keys()
for x in highRiskCon[0]:
    ch = ord(x[0]) - ord('a')
    chv = x[1:]
    mapKeys = list(filter(lambda d: d.split('-')[ch] == chv, mapKeys))


attrChars = [chr(ord('a') + i) for i in range(attrNum)]
attrChars.remove(chr(ord('a') + sensitiveAttrIdx))
allCombination = []
for an in range(1, len(attrChars)+1):
    attrSets = list(itertools.combinations(attrChars, an))
    allCombination.extend(attrSets)

mapKeys = list(map(lambda d: d.split('-'), mapKeys))

kMapKey = list(filter(lambda d: d[sensitiveAttrIdx] == '1', mapKeys))
nkMapKey = list(filter(lambda d: d[sensitiveAttrIdx] == '0', mapKeys))
start = time.time()
ret = {}
for attrSet in allCombination:
    attrIdx = tuple(map(lambda d: ord(d) - ord('a'), attrSet))
    attrV1 = set(['-'.join(map(lambda i: k[i], attrIdx)) for k in kMapKey])
    attrV2 = set(['-'.join(map(lambda i: k[i], attrIdx)) for k in nkMapKey])
    attrV = list(attrV1 - attrV2)
    if len(attrV) > 0:
        ret[attrIdx] = attrV
end = time.time()
print('算法运行时间', end - start)
print(ret)



print(allCombination)
highRiskRec = defaultdict(list)
attrSetIdxMap = defaultdict(list)
DC2C = dict()
mapKeys = cntMap.keys()
minSensitivity = defaultdict(dict)
for X in highRiskCon:
    nx = len(X)
    # 1. 属性集合大小为 nx 的情况
    for i in range(nx):
        removeIdx = ord(X[i][0]) - ord('a')
        removeV = X[i][1:]
        c = list(X.copy())
        c.remove(X[i])
        candidate = victimKey
        # candAttrs = list(allCombination.copy())
        attrSet = list()
        for it in c:
            idx = ord(it[0]) - ord('a')
            v = it[1:]
            candidate = list(filter(lambda d: d.split('-')[idx] == v and d.split('-')[removeIdx] != removeV and len(cntMap[d]) == 1, candidate))
        attrSet = list(map(lambda d: d[0], X))
        attrSet.sort()
            # candAttrs = list(filter(lambda d: it[0] in d, candAttrs))
        for can in candidate:
            curKey = can
            curKeyA = curKey.split('-')

            # for attrSet in candAttrs:
            find = False
            findAttr = []
            attrIdxSet = [ord(j) - ord('a') for j in attrSet]
            for mk in mapKeys:
                if mk == curKey:
                    continue
                else:
                    mka = mk.split('-')
                    # 判断是否是该属性集合的潜在受害者
                    for ai in attrIdxSet:
                        if mka[ai] != curKeyA[ai]:
                            break
                    else:
                        find = True
                        break
            if not find:
                pvi = cntMap[can][0]
                findAttr = attrSet
                attrSetIdxMap[tuple(findAttr)].append(pvi)
                findAttrName = [attrs[ord(c) - ord('a')] for c in findAttr]

                # 更新局部敏感度
                secondQueryGroup = list(cntMap.keys())
                for it in X:
                    idx = ord(it[0]) - ord('a')
                    v = it[1:]
                    secondQueryGroup = list(filter(lambda d: d.split('-')[idx] == v, secondQueryGroup))
                # DC2C[tuple(findAttrName)] = tuple()
                    # highRiskIdx = cntMap[can][0]
                # print(secondQueryGroup)
                MaxS = 0
                for key in secondQueryGroup:
                    S = rawValues[max(cntMap[key], key=lambda d: rawValues[d][sensitiveAttrIdx])][sensitiveAttrIdx]
                    MaxS = max(S, MaxS)
                minSensitivity[pvi][nx] = minSensitivity[pvi].get(nx, MaxS)
                minSensitivity[pvi][nx] = min(MaxS, minSensitivity[pvi][nx])
                # print(minSensitivity)
            # firstCond = list(map(lambda d: d[0], c))
            # secondCond = list(firstCond.copy())
            # secondCond.append(X[i][0])
            # highRiskRec[highRiskIdx].append([firstCond, secondCond])

    # 2. 属性集合大小大于 nx 的情况
    for i in range(nx+1, attrNum):
        # a. 高风险条件满足，额外属性集合不满足
        attrSets = list(itertools.combinations(attrChars, i))
        candidate = victimKey
        Xattrs = list(map(lambda d: d[0], X))
        Xattrs.sort()
        for it in X:
            idx = ord(it[0]) - ord('a')
            v = it[1:]
            candidate = list(filter(lambda d: d.split('-')[idx] == v and len(cntMap[d]) == 1, candidate))
            attrSets = list(filter(lambda d: it[0] in d, attrSets))


            # candAttrs = list(filter(lambda d: it[0] in d, candAttrs))
        for can in candidate:
            curKey = can
            curKeyA = curKey.split('-')

            for attrSet in attrSets:
                otherAttrs = list(set(attrSet) - set(Xattrs))
                find = False
                findAttr = []
                attrIdxSet = [ord(j) - ord('a') for j in attrSet]
                for oa in otherAttrs:
                    differAttrSet = list(attrSet)
                    removeIdx = ord(oa) - ord('a')
                    removeV = curKeyA[removeIdx]
                    differAttrSet.remove(oa)
                    differAttrIdSet = [ord(j) - ord('a') for j in differAttrSet]
                    differAttrV = [j + str(curKeyA[differAttrIdSet[dasi]]) for dasi, j in enumerate(differAttrSet)]
                    differCount = 0
                    for mk in mapKeys:
                        if mk == curKey:
                            continue
                        else:
                            mka = mk.split('-')
                            # 判断是否是该属性集合的潜在受害者
                            for ai in attrIdxSet:
                                if mka[ai] != curKeyA[ai]:
                                    break
                            else:
                                find = True
                                break
                            # 判断第二次查询是否大小为 0 或 1
                            for ai in differAttrIdSet:
                                if mka[ai] != curKeyA[ai]:
                                    pass
                            else:
                                differCount += 1

                    if not find and differCount > 0:
                        pvi = cntMap[can][0]
                        findAttr = attrSet
                        if len(attrSetIdxMap[tuple(findAttr)]) == 0 or attrSetIdxMap[tuple(findAttr)][-1] != cntMap[can][0]:

                            attrSetIdxMap[tuple(findAttr)].append(pvi)
                            findAttrName = [attrs[ord(c) - ord('a')] for c in findAttr]

                        # 更新局部敏感度
                        secondQueryGroup = list(cntMap.keys())
                        for it in differAttrV:
                            idx = ord(it[0]) - ord('a')
                            v = it[1:]
                            secondQueryGroup = list(
                                filter(lambda d: d.split('-')[idx] == v and d.split('-')[removeIdx] != removeV,
                                       secondQueryGroup))
                        # DC2C[tuple(findAttrName)] = tuple()
                        # highRiskIdx = cntMap[can][0]
                        # print(secondQueryGroup)
                        minSG = defaultdict(list)
                        for sqi in secondQueryGroup:
                            sqidx = cntMap[sqi][0]
                            gid = sqi.split('-')[removeIdx]
                            minSG[gid].append(sqidx)
                        for gid in minSG.keys():
                            if len(minSG[gid]) > 1:
                                S = rawValues[max(minSG[gid], key=lambda d: rawValues[d][sensitiveAttrIdx])][
                                    sensitiveAttrIdx]
                                minSensitivity[pvi][i] = minSensitivity[pvi].get(i, S)
                                minSensitivity[pvi][i] = min(S, minSensitivity[pvi][i])

    for i in range(nx + 1, attrNum):
        # b. 高风险条件部分满足，额外属性集合满足
        attrSets = list(itertools.combinations(attrChars, i))
        candidate = victimKey
        Xattrs = list(map(lambda d: d[0], X))
        Xattrs.sort()

        for j in range(nx):
            removeIdx = ord(X[j][0]) - ord('a')
            removeV = X[j][1:]
            c = list(X.copy())
            c.remove(X[j])
            for it in c:
                idx = ord(it[0]) - ord('a')
                v = it[1:]
                candidate = list(filter(lambda d: d.split('-')[idx] == v and d.split('-')[removeIdx] != removeV and len(cntMap[d]) == 1, candidate))
                attrSets = list(filter(lambda d: it[0] in d, attrSets))
            attrSets = list(filter(lambda d: X[j][0] in d, attrSets))

                # candAttrs = list(filter(lambda d: it[0] in d, candAttrs))
            for can in candidate:
                curKey = can
                curKeyA = curKey.split('-')

                for attrSet in attrSets:
                    otherAttrs = Xattrs
                    find = False
                    findAttr = []
                    attrIdxSet = [ord(j) - ord('a') for j in attrSet]
                    oa = X[j][0]
                    differAttrSet = list(attrSet)
                    differAttrSet.remove(oa)
                    differAttrIdSet = [ord(j) - ord('a') for j in differAttrSet]
                    differAttrV = [j + str(curKeyA[differAttrIdSet[dasi]]) for dasi, j in enumerate(differAttrSet)]
                    differCount = 0
                    for mk in mapKeys:
                        if mk == curKey:
                            continue
                        else:
                            mka = mk.split('-')
                            # 判断是否是该属性集合的潜在受害者
                            for ai in attrIdxSet:
                                if mka[ai] != curKeyA[ai]:
                                    break
                            else:
                                find = True
                                break
                            # 判断第二次查询是否大小为 0 或 1
                            for ai in differAttrIdSet:
                                if mka[ai] != curKeyA[ai]:
                                    pass
                            else:
                                differCount += 1

                    if not find and differCount > 0:
                        findAttr = attrSet
                        pvi = cntMap[can][0]
                        if len(attrSetIdxMap[tuple(findAttr)]) == 0 or attrSetIdxMap[tuple(findAttr)][-1] != cntMap[can][0]:
                            attrSetIdxMap[tuple(findAttr)].append(pvi)
                            findAttrName = [attrs[ord(c) - ord('a')] for c in findAttr]

                        # 更新局部敏感度
                        secondQueryGroup = list(cntMap.keys())
                        for it in differAttrV:
                            idx = ord(it[0]) - ord('a')
                            v = it[1:]
                            secondQueryGroup = list(
                                filter(lambda d: d.split('-')[idx] == v and d.split('-')[removeIdx] != removeV,
                                       secondQueryGroup))
                        # DC2C[tuple(findAttrName)] = tuple()
                        # highRiskIdx = cntMap[can][0]
                        # print(secondQueryGroup)
                        minSG = defaultdict(list)
                        for sqi in secondQueryGroup:
                            sqidx = cntMap[sqi][0]
                            gid = sqi.split('-')[removeIdx]
                            minSG[gid].append(sqidx)
                        for gid in minSG.keys():
                            if len(minSG[gid]) > 1:
                                S = rawValues[max(minSG[gid], key=lambda d: rawValues[d][sensitiveAttrIdx])][
                                    sensitiveAttrIdx]
                                minSensitivity[pvi][i] = minSensitivity[pvi].get(i, S)
                                minSensitivity[pvi][i] = min(S, minSensitivity[pvi][i])

print(attrSetIdxMap)
print('minSensitivity: ', minSensitivity)
for key in attrSetIdxMap.keys():
    attrSetIdxMap[key] = list(set(attrSetIdxMap[key]))
    # if len(attrSetIdxMap[key]) != len(set(attrSetIdxMap[key])):
    #     print('xxxxx')
ASIM = dict(attrSetIdxMap)
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

for i in IASM.keys():
    for an in minSensitivity[i].keys():
        S1 = max(minSensitivity[i][an], rawValues[i][sensitiveAttrIdx])
        S2 = minSensitivity[i][an]
        D = rawValues[i][sensitiveAttrIdx] * dp
        riskMap[i][an] = laplace_DV_P2([-D, D], S1/epsilon, S2/epsilon)

attrs.remove(attrs[sensitiveAttrIdx])
data = {
    'attrs': attrs,
    'IASM': IASM,
    'RM': riskMap
}

end = time.time()
print('运行时间:', end-start)

charges = list(charges)
left, right = charges[0], charges[-1]
# S = charges
X = charges
dp = 0.2
epsilon = 1

# x1, x2, x3, x4, x5 = left, charges[n//4], charges[n//2], charges[3*n//4], right
#
# Y1 = [laplace_DV_P2([-x1*dp, x1*dp], max(x1/epsilon, s/epsilon), s/epsilon) for s in S]
# Y2 = [laplace_DV_P2([-x2*dp, x2*dp], max(x2/epsilon, s/epsilon), s/epsilon) for s in S]
# Y3 = [laplace_DV_P2([-x3*dp, x3*dp], max(x3/epsilon, s/epsilon), s/epsilon) for s in S]
# Y4 = [laplace_DV_P2([-x4*dp, x4*dp], max(x4/epsilon, s/epsilon), s/epsilon) for s in S]
# Y5 = [laplace_DV_P2([-x5*dp, x5*dp], max(x5/epsilon, s/epsilon), s/epsilon) for s in S]
S1, S2, S3, S4, S5 = left, charges[n//4], charges[n//2], charges[3*n//4], right
if S1 == 0:
    S1 = 0.1
Y1 = [laplace_DV_P2([-x*dp, x*dp], max(x/epsilon, S1/epsilon), S1/epsilon) for x in X]
Y2 = [laplace_DV_P2([-x*dp, x*dp], max(x/epsilon, S2/epsilon), S2/epsilon) for x in X]
Y3 = [laplace_DV_P2([-x*dp, x*dp], max(x/epsilon, S3/epsilon), S3/epsilon) for x in X]
Y4 = [laplace_DV_P2([-x*dp, x*dp], max(x/epsilon, S4/epsilon), S4/epsilon) for x in X]
Y5 = [laplace_DV_P2([-x*dp, x*dp], max(x/epsilon, S5/epsilon), S5/epsilon) for x in X]
#
plt.plot(X, Y1, '-o', label="minV")
plt.plot(X, Y2, '-o', label="1/4V")
plt.plot(X, Y3, '-o', label="midV")
plt.plot(X, Y4, '-o', label="3/4V")
plt.plot(X, Y5, '-o', label="maxV")
plt.legend()
plt.show()
# print(data)
# with open("data/Ldata.json", "w", encoding="utf-8") as f:
#     f.write(json.dumps(data, indent=4))
# for hrr in highRiskRec:
#     print(cntMap[hrr])
# print(highRiskRec)



