import itertools
import json
import time
from collections import defaultdict

import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render

from HighRisk.utils import laplace_DV_P2, listIncluded, laplace_DV_P
from RiskTree.funcs import getDataCoder, key2string, getCodedData


# Create your views here.
def highRiskData(request):
    postData = json.loads(request.body)
    filename = postData['filename']
    attrList = postData['attrList']
    attrNameList = list(map(lambda d: d['Attribute'], attrList))
    sensitivityWay = postData['sensitivityWay']
    TopNum = postData['TopNum']
    QueryType = postData['QueryType']
    epsilon = postData['epsilon']
    deviationRatio = postData['deviationRatio']
    qc = postData['QueryContent']
    VictimFilter = postData['VictimFilter']
    df = pd.read_csv('data/{0}'.format(filename))
    df = df[attrNameList]
    if sensitivityWay == 'Global sensitivity' or sensitivityWay == 'Global':
        ret = GlobalAlgorithm(df, qc, attrList, TopNum, QueryType, epsilon, deviationRatio, VictimFilter)
    else:
        ret = LocalAlgorithm(df, qc, attrList, TopNum, QueryType, epsilon, deviationRatio, VictimFilter)
    return JsonResponse({'data': ret})


def ValueFilter(values, VictimfilterScope, ATTRS):
    if VictimfilterScope == {}:
        return values
    for attr, s in VictimfilterScope.items():
        idx = ATTRS.index(attr)
        if len(s) == 2 and type(s[0]) != str:
            # 数值型
            values = list(filter(lambda d: s[0] - 1 <= d[idx] <= s[1] + 1, values))
        else:
            values = list(filter(lambda d: d[idx] in s, values))
    return values

def getKeyMap(request):
    postData = json.loads(request.body)
    filename = postData['filename']
    attrList = postData['attrList']
    indices = postData['indices']

    global m, DCs, R
    R = pd.read_csv('data/' + filename)

    keepAttr = list(map(lambda d: d['Attribute'], attrList))
    cur_keepAttr = [keepAttr[i] for i in indices]
    cur_attrList = [attrList[i] for i in indices]

    R = R[cur_keepAttr]
    R.fillna(0, inplace=True)
    n = R.shape[0]
    m = R.shape[1]
    DCs = getDataCoder(R, cur_attrList)
    values = R.values
    getCodedData(values, DCs, cur_keepAttr)

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
    json_data = {
        'keyMap': keyMap,
    }

    return JsonResponse(json_data)

def GlobalAlgorithm(df, qc, attrList, TopNum, QueryType, epsilon, deviationRatio, VictimFilter):
    start = time.time()
    [VictimFilterScope, AttrFilter] = VictimFilter
    IncludeAttr = list(filter(lambda d: AttrFilter[d] == 'include', AttrFilter.keys()))
    ExcludeAttr = list(filter(lambda d: AttrFilter[d] == 'exclude', AttrFilter.keys()))
    # df.drop('ID', axis=1, inplace=True)
    attrs = df.columns.tolist()
    df.fillna(0, inplace=True)
    sortedIdx = df.sort_values(by=qc, ascending=False).index
    rawValues = df.values
    end = time.time()
    print("排序运行时间:", end - start, '秒')
    sensitiveAttr = qc
    sensitiveAttrIdx = attrs.index(sensitiveAttr)
    DCs = getDataCoder(df, attrList)
    values = df.values
    isCategorical = type(values[0][sensitiveAttrIdx]) == str
    QueryType = 'count' if isCategorical else 'sum'
    getCodedData(values, DCs, attrs, '' if isCategorical else sensitiveAttr)


    # 过滤属性范围

    n = len(values)

    print(df.columns.tolist())


    cntMap = defaultdict(list)
    specialCntMap = defaultdict(list)
    idxKeyMap = {}
    idxSpecialKeyMap = {}
    attrKeyRange = {}
    for i, d in enumerate(values):
        key = '-'.join(str(int(v)) for v in d.tolist())
        specialKey = '-'.join(str(int(v)) for (idx, v) in enumerate(d.tolist()) if idx != sensitiveAttrIdx)
        cntMap[key].append(i)
        specialCntMap[specialKey].append(i)
        idxKeyMap[i] = key
        idxSpecialKeyMap[i] = specialKey
        for vi, v in enumerate(d):
            attrKeyRange[vi] = attrKeyRange.get(vi, [int(v), int(v)])
            attrKeyRange[vi][0] = min(attrKeyRange[vi][0], int(v))
            attrKeyRange[vi][1] = max(attrKeyRange[vi][1], int(v))

    riskRecord = []
    for skey in specialCntMap.keys():
        if len(specialCntMap[skey]) == 1:
            riskRecord.append(specialCntMap[skey][0])

    MaxS = 0
    attrNum = len(attrs)
    attrChars = [chr(ord('a') + i) for i in range(attrNum)]
    attrChars.remove(chr(ord('a') + sensitiveAttrIdx))
    # 去除不包括属性
    for ea in ExcludeAttr:
        attrChars.remove(chr(ord('a') + attrs.index(ea)))
    attrSetIdxMap = defaultdict(list)
    Attack = defaultdict(list)
    mapKeys = cntMap.keys()
    candidateRecord = {}
    mapKeysL = list(map(lambda d: d.split('-'), mapKeys))
    dp = deviationRatio  # deviation percent
    combList = []
    for an in range(1, len(attrChars) + 1):
        comb = itertools.combinations(attrChars, an)
        combList.append(list(comb))
    if QueryType == 'sum':
        for si in range(n):
            MaxS = max(MaxS, rawValues[si][sensitiveAttrIdx])
    else:
        MaxS = 1


    t1 = 0
    t2 = 0
    mapKeysL = list(map(lambda d: d.split('-'), mapKeys))
    finishedAn = []
    for pvi in sortedIdx:

        curspecialKey = idxSpecialKeyMap[pvi]
        curKey = idxKeyMap[pvi]
        curKeyA = curKey.split('-')
        for ani in range(attrNum-1):
            if ani+1 not in finishedAn and len(Attack[ani+1]) >= TopNum:
                finishedAn.append(ani+1)
        if len(finishedAn) == attrNum-1:
            break
        if len(specialCntMap[curspecialKey]) == 1:
            # 判断个体是否在用户指定的范围内
            if len(ValueFilter([rawValues[pvi]], VictimFilterScope, attrs)) == 0:
                continue

            for combi, comb in enumerate(combList):
                an = combi + 1
                if pvi == 534 and an == 2:
                    print('xxx')
                if an in finishedAn:
                    continue


                for attrSet in comb:
                    attrIdxSet = [ord(j) - ord('a') for j in attrSet]
                    findAttrName = [attrs[idx] for idx in attrIdxSet]
                    isContent = True
                    for ia in IncludeAttr:
                        if ia not in findAttrName:
                            isContent = False
                            break
                    if isContent == False:
                        continue
                    find = False
                    findAttr = []

                    keyL = [curKeyA[idx] for idx in attrIdxSet]

                    s2 = time.time()
                    curCon = []
                    QueryGroup = []
                    QueryGroup = mapKeysL
                    for ai in attrIdxSet:
                        curCon.append((ai, int(curKeyA[ai])))
                        if candidateRecord.get(tuple(curCon), 0) == 0:
                            QueryGroup = list(
                                filter(lambda d: int(curKeyA[ai]) == int(d[ai]),
                                       QueryGroup))
                            candidateRecord[tuple(curCon)] = QueryGroup

                        else:
                            QueryGroup = candidateRecord.get(tuple(curCon))
                    if len(QueryGroup) != 1:
                        find = True
                    e2 = time.time()
                    t2 += e2 - s2
                    if not find:
                        findAttr = attrSet
                        attrSetIdxMap[findAttr].append(pvi)



                        if QueryType == 'sum':
                            if pvi == 543:
                                print('xxx')
                            D = rawValues[pvi][sensitiveAttrIdx] * dp
                            risk = laplace_DV_P([-D, D], MaxS / epsilon)
                        else:
                            risk = laplace_DV_P([-0.5, 0], MaxS / epsilon) + 0.5
                        # 计算第二次查询情况
                        attrIdx = attrIdxSet
                        findQuery = False

                        for differAttr in attrIdx:
                            differVal = 1
                            curIdx = 1
                            s1 = time.time()
                            while -attrKeyRange[differAttr][1] <= differVal <= attrKeyRange[differAttr][1]:
                                secondQueryGroup = mapKeysL
                                curCon = []
                                for i, attr in enumerate(attrIdx):
                                    if attr == differAttr:
                                        secondKey = int(keyL[i]) + differVal
                                        if 0 <= secondKey <= attrKeyRange[differAttr][1]:
                                            if differVal > 0:
                                                curCon.append((attr, int(keyL[i])+1, secondKey))
                                            else:
                                                curCon.append((attr, secondKey, int(keyL[i]) - 1))
                                            if candidateRecord.get(tuple(curCon), 0) == 0:
                                                if differVal > 0:
                                                    secondQueryGroup = list(
                                                        filter(lambda d: int(keyL[i]) < int(d[attr]) <= secondKey,
                                                               secondQueryGroup))
                                                    candidateRecord[tuple(curCon)] = secondQueryGroup
                                                else:
                                                    secondQueryGroup = list(
                                                        filter(lambda d: secondKey <= int(d[attr]) < int(keyL[i]),
                                                               secondQueryGroup))
                                                    candidateRecord[tuple(curCon)] = secondQueryGroup
                                            else:
                                                secondQueryGroup = candidateRecord.get(tuple(curCon))
                                        else:
                                            secondQueryGroup = []
                                            break
                                    else:
                                        curCon.append((attr, int(keyL[i])))
                                        if candidateRecord.get(tuple(curCon), 0) == 0:
                                            secondQueryGroup = list(
                                                filter(lambda d: d[attr] == keyL[i], secondQueryGroup))
                                            candidateRecord[tuple(curCon)] = secondQueryGroup
                                        else:
                                            secondQueryGroup = candidateRecord.get(tuple(curCon))

                                secondQueryGroupIdx = []
                                for secondK in secondQueryGroup:
                                    secondQueryGroupIdx.extend(cntMap['-'.join(secondK)])
                                secondQueryGroupIdx = list(set(secondQueryGroupIdx))
                                if len(secondQueryGroupIdx) > 1:
                                    Attack[len(findAttr)].append(
                                        [pvi, findAttrName, attrs[differAttr], MaxS, secondQueryGroupIdx, keyL, risk])
                                    findQuery = True
                                # len(secondQueryGroupIdx) == 1 本应有更好的处理
                                elif len(secondQueryGroupIdx) == 0 or len(secondQueryGroupIdx) == 1:
                                    if differVal > 0:
                                        differVal = differVal - curIdx
                                    else:
                                        differVal = differVal + curIdx
                                    curIdx += 1

                                if findQuery:
                                    break
                            e1 = time.time()
                            t1 += e1 - s1
                            if findQuery:
                                break
    print('t2 运行时间：', t2)
    print('t1 运行时间：', t1)

    end = time.time()
    print("寻找攻击运行时间:", end - start, '秒')

    # for an in Attack.keys():
    #     Attack[an].sort(key=lambda d: -d[-1])
    #     Attack[an] = Attack[an][0:TopNum]

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



    print(riskMap)
    for an in Attack.keys():
        Attack[an] = Attack[an][0:TopNum]
    attrs.remove(attrs[sensitiveAttrIdx])
    data = {
        'attrs': attrs,
        'Attack': Attack,
        'riskRecord': riskRecord
    }


    end = time.time()
    print("运行时间:", end - start, '秒')
    return data


def LocalAlgorithm(df, qc, attrList, TopNum, QueryType, epsilon, deviationRatio, VictimFilter):
    [VictimFilterScope, AttrFilter] = VictimFilter
    IncludeAttr = list(filter(lambda d: AttrFilter[d] == 'include', AttrFilter.keys()))
    ExcludeAttr = list(filter(lambda d: AttrFilter[d] == 'exclude', AttrFilter.keys()))
    # df.drop('ID', axis=1, inplace=True)
    attrs = df.columns.tolist()
    attrNum = len(attrs)
    df.fillna(0, inplace=True)
    rawValues = df.values

    n = len(rawValues)

    # sensitiveAttr = 'Income'
    sensitiveAttr = qc
    sensitiveAttrIdx = attrs.index(sensitiveAttr)
    charges = df[sensitiveAttr].sort_values()
    thresholdList = []
    for i in range(6):
        idx = i * n // 5
        if i == 5:
            idx -= 1
        thresholdList.append(charges[idx])

    start = time.time()

    DCs = getDataCoder(df, attrList)
    codedValues = df.values
    isCategorical = type(codedValues[0][sensitiveAttrIdx]) == str
    QueryType = 'count' if isCategorical else 'sum'
    getCodedData(codedValues, DCs, attrs, '' if isCategorical else sensitiveAttr)
    valuesList = []
    Attack = defaultdict(list)
    attrKeyRange = {}
    temp = {}
    for i in range(5):
        curValues = list(codedValues.copy())
        for attrI, attr in enumerate(attrs):
            if attr == sensitiveAttr:
                for j in range(n):
                    curValues[j][attrI] = 0 <= codedValues[j][attrI] <= thresholdList[i+1]
        valuesList.append(curValues)
    preSpecialCon = {}
    notContentNumL = list(range(1, attrNum+1))
    for valuesIdx, curValues in enumerate(valuesList):
        if len(notContentNumL) == 0:
            break
        cntMap = defaultdict(list)
        specialCntMap = defaultdict(list)
        idxKeyMap = {}
        for i, d in enumerate(curValues):
            key = '-'.join(str(int(v)) for v in d.tolist())
            cntMap[key].append(i)
            specialKey = '-'.join(str(int(v)) for (idx, v) in enumerate(d.tolist()) if idx != sensitiveAttrIdx)
            specialCntMap[specialKey].append(i)
            idxKeyMap[i] = key
            if attrKeyRange == {}:
                for vi, v in enumerate(d):
                    temp[vi] = temp.get(vi, [int(v), int(v)])
                    temp[vi][0] = min(temp[vi][0], int(v))
                    temp[vi][1] = max(temp[vi][1], int(v))
        attrKeyRange = temp

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
        # 去除不包括属性
        for ea in ExcludeAttr:
            attrChars.remove(chr(ord('a') + attrs.index(ea)))
        allCombination = []
        for an in range(1, len(attrChars) + 1):
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
            attrV = attrV1 - attrV2
            attrVL = list(attrV)
            if len(attrV) > 0:
                specialCon[attrIdx] = attrVL
                if attrIdx in preSpecialCon.keys():
                    specialCon[attrIdx] = attrV - set(preSpecialCon[attrIdx])
        preSpecialCon = specialCon


        minSensitivity = defaultdict(dict)
        attrSetIdxMap = defaultdict(list)

        t1 = 0
        t2 = 0
        t3 = 0
        t4 = 0


        candidateRecord = {}
        # 遗失一种特殊情况是  相邻描述 为空，再相邻
        for attrIdx in specialCon.keys():
            if len(attrIdx) not in notContentNumL:
                continue
            for key in specialCon[attrIdx]:
                keyL = key.split('-')
                for differAttr in attrIdx:
                    for differVal in [1, -1]:
                        candidate = mapKeys
                        s1 = time.time()
                        curCon = []
                        specialKeyL = list(keyL.copy())
                        for i, attr in enumerate(attrIdx):
                            if attr == differAttr:
                                curCon.append((attr, int(keyL[i]) + differVal))
                                specialKeyL[i] = int(specialKeyL[i]) + differVal
                                if candidateRecord.get(tuple(curCon), 0) == 0:
                                    candidate = list(filter(lambda d: int(d[attr]) == int(keyL[i]) + differVal, candidate))
                                    candidateRecord[tuple(curCon)] = candidate
                                else:
                                    candidate = candidateRecord.get(tuple(curCon))

                            else:
                                curCon.append((attr, int(keyL[i])))
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
                                if len(ValueFilter([rawValues[pvi]], VictimFilterScope, attrs)) == 0:
                                    continue
                                findAttr = list(map(lambda d: attrs[d], attrIdx))
                                isContent = True
                                for ia in IncludeAttr:
                                    if ia not in findAttr:
                                        isContent = False
                                        break
                                if isContent == False:
                                    continue
                                attrSetIdxMap[tuple(findAttr)].append(pvi)

                                # 更新局部敏感度
                                if differVal > 0:
                                    differVRange = [0, -100, -1]
                                else:
                                    differVRange = [0, 100, 1]
                                for differV in range(*differVRange):
                                    secondQueryGroup = mapKeys
                                    curCon = []
                                    DV = int(keyL[i]) + differV
                                    for i, attr in enumerate(attrIdx):
                                        if attr == differAttr:
                                            if differV >= 0:
                                                curCon.append((attr, (int(keyL[i]), int(keyL[i]) + differV)))
                                                if candidateRecord.get(tuple(curCon), 0) == 0:
                                                    secondQueryGroup = list(
                                                        filter(lambda d: int(keyL[i]) <= int(d[attr]) <= int(keyL[i]) + differV,
                                                               secondQueryGroup))
                                                    candidateRecord[tuple(curCon)] = secondQueryGroup
                                                else:
                                                    secondQueryGroup = candidateRecord.get(tuple(curCon))
                                            else:
                                                curCon.append((attr, ((int(keyL[i]) + differV), int(keyL[i]))))
                                                if candidateRecord.get(tuple(curCon), 0) == 0:
                                                    secondQueryGroup = list(
                                                        filter(lambda d: int(keyL[i]) + differV <= int(d[attr]) <= int(
                                                            keyL[i]),
                                                               secondQueryGroup))
                                                    candidateRecord[tuple(curCon)] = secondQueryGroup
                                                else:
                                                    secondQueryGroup = candidateRecord.get(tuple(curCon))
                                        else:
                                            curCon.append((attr, int(keyL[i])))
                                            if candidateRecord.get(tuple(curCon), 0) == 0:
                                                secondQueryGroup = list(filter(lambda d: d[attr] == keyL[i], secondQueryGroup))
                                                candidateRecord[tuple(curCon)] = secondQueryGroup
                                            else:
                                                secondQueryGroup = candidateRecord.get(tuple(curCon))
                                    MaxS = 0
                                    secondQueryGroupIdx = []
                                    for secondK in secondQueryGroup:
                                        S = \
                                        rawValues[max(cntMap['-'.join(secondK)], key=lambda d: rawValues[d][sensitiveAttrIdx])][
                                            sensitiveAttrIdx]
                                        MaxS = max(S, MaxS)
                                        secondQueryGroupIdx.extend(cntMap['-'.join(secondK)])
                                    secondQueryGroupIdx = list(set(secondQueryGroupIdx))
                                    if len(secondQueryGroupIdx) > 1:
                                        nx = len(attrIdx)
                                        minSensitivity[pvi][nx] = minSensitivity[pvi].get(nx, MaxS)
                                        minSensitivity[pvi][nx] = min(MaxS, minSensitivity[pvi][nx])
                                        if len(list(filter(lambda d: d[0] == pvi, Attack[nx]))) == 0:
                                            Attack[nx].append([pvi, findAttr, attrs[differAttr], minSensitivity[pvi][nx], secondQueryGroupIdx, specialKeyL])
                                        break
                                    else:
                                        if DV > attrKeyRange[differAttr][1] or DV < attrKeyRange[differAttr][0]:
                                            break

                            e2 = time.time()
                            t2 += e2 - s2




        riskMap = defaultdict(dict)
        dp = deviationRatio  # deviation percent

        for nx, ats in Attack.items():
            for i in range(len(ats)):
                pvi = ats[i][0]
                riskV = rawValues[pvi][sensitiveAttrIdx]
                S1 = max(ats[i][3], riskV)
                S2 = ats[i][3]
                if S2 == 0:
                    S2 += 0.1

                if QueryType == 'sum':
                    D = riskV * dp
                    risk = laplace_DV_P2([-D, D], S1 / epsilon, S2 / epsilon)
                else:
                    risk = laplace_DV_P([-0.5, 0], 1 / epsilon) + 0.5
                ats[i].append(risk)
            Attack[nx].sort(key=lambda d: -d[-1])
        print(Attack)

        charges = list(charges)
        left, right = charges[0], charges[-1]
        maxRisk = laplace_DV_P2([-right * dp, right * dp], max(right / epsilon, thresholdList[valuesIdx+1] / epsilon), thresholdList[valuesIdx+1] / epsilon)


        for nx, ats in Attack.items():
            if len(ats) < TopNum:
                if nx in notContentNumL:
                    notContentNumL.remove(nx)
            elif QueryType == 'sum':
                if ats[TopNum-1][-1] >= maxRisk:
                    pass
                else:
                    if nx in notContentNumL:
                        notContentNumL.remove(nx)

    # test = defaultdict(list)
    # victimList = defaultdict(list)
    # for an in notContentNumL:
    #     attrSets = list(itertools.combinations(attrChars, an))
    #     for curKey in victimKey:
    #         curKeyA = curKey.split('-')
    #         keyL = curKeyA
    #
    #         for attrSet in attrSets:
    #             find = False
    #             findAttr = []
    #             attrIdxSet = [ord(j) - ord('a') for j in attrSet]
    #             for mkl in mapKeys:
    #                 mk = '-'.join(mkl)
    #                 if mk == curKey:
    #                     continue
    #                 else:
    #                     mka = mk.split('-')
    #                     for ai in attrIdxSet:
    #                         if mka[ai] != curKeyA[ai]:
    #                             break
    #                     else:
    #                         find = True
    #                         break
    #             if not find:
    #                 pvi = cntMap[curKey][0]
    #                 if len(ValueFilter([rawValues[pvi]], VictimFilterScope, attrs)) == 0:
    #                     continue
    #                 findAttr = attrSet
    #                 findAttrName = [attrs[j] for j in attrIdxSet]
    #                 isContent = True
    #                 for ia in IncludeAttr:
    #                     if ia not in findAttrName:
    #                         isContent = False
    #                         break
    #                 if isContent == False:
    #                     continue
    #                 test[findAttr].append(pvi)
    #
    #                 # 更新风险
    #
    #                 attrIdx = attrIdxSet
    #                 for differAttr in attrIdx:
    #                     for differVal in [1, -1]:
    #                         secondQueryGroup = mapKeys
    #                         curCon = []
    #                         for i, attr in enumerate(attrIdx):
    #                             if attr == differAttr:
    #                                 curCon.append((attr, int(keyL[i]) + differVal))
    #                                 if candidateRecord.get(tuple(curCon), 0) == 0:
    #                                     secondQueryGroup = list(
    #                                         filter(lambda d: int(d[attr]) == int(keyL[i]) + differVal,
    #                                                secondQueryGroup))
    #                                     candidateRecord[tuple(curCon)] = secondQueryGroup
    #                                 else:
    #                                     secondQueryGroup = candidateRecord.get(tuple(curCon))
    #                             else:
    #                                 curCon.append((attr, int(keyL[i])))
    #                                 if candidateRecord.get(tuple(curCon), 0) == 0:
    #                                     secondQueryGroup = list(filter(lambda d: d[attr] == keyL[i], secondQueryGroup))
    #                                     candidateRecord[tuple(curCon)] = secondQueryGroup
    #                                 else:
    #                                     secondQueryGroup = candidateRecord.get(tuple(curCon))
    #                         MaxS = 0
    #                         secondQueryGroupIdx = []
    #                         for secondK in secondQueryGroup:
    #                             S = \
    #                             rawValues[max(cntMap['-'.join(secondK)], key=lambda d: rawValues[d][sensitiveAttrIdx])][
    #                                 sensitiveAttrIdx]
    #                             MaxS = max(S, MaxS)
    #                             secondQueryGroupIdx.extend(cntMap['-'.join(secondK)])
    #                         secondQueryGroupIdx = list(set(secondQueryGroupIdx))
    #                         if len(secondQueryGroupIdx) > 1:
    #                             victimList[an].append(pvi)
    #                             if MaxS >= threshold:
    #                                 if MaxS == 0:
    #                                     MaxS += 0.1
    #                                 curV = rawValues[pvi][sensitiveAttrIdx]
    #                                 risk = laplace_DV_P2([-curV * dp, curV * dp], max(curV / epsilon, MaxS / epsilon),
    #                                                      MaxS / epsilon)
    #                                 NumRiskMap[an].append(risk)
    #
    #                                 filterAttack = list(filter(lambda d: d[0] == pvi, Attack[an]))
    #                                 if len(filterAttack) == 0:
    #                                     Attack[an].append([pvi, findAttrName, attrs[differAttr], MaxS, secondQueryGroupIdx, keyL, risk])
    #                                 else:
    #                                     filterAttack[0][-1] = max(filterAttack[0][-1], risk)
    #                                     filterAttack[0][-4] = min(filterAttack[0][-4], MaxS)
    #
    #     Attack[an].sort(key=lambda d: -d[-1])
    #
    #     # print(NumRiskMap[an])
    #     NumRiskMap[an].sort(key=lambda d: -d)
        # print(NumRiskMap[an])

    for an in Attack.keys():
        Attack[an] = Attack[an][0:TopNum]
    attrs.remove(attrs[sensitiveAttrIdx])
    data = {
        'attrs': attrs,
        'Attack': Attack,
    }

    return data
