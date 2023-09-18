from typing import Union

import numpy as np
import pandas as pd
import statistics as s


class DFProcessor:
    def __init__(self, data_filepath, attr, QueryCondition, sensitivityWay, attrParams=None):
        self._df = pd.read_csv('data/' + data_filepath, sep=",")
        self._df.fillna(0, inplace=True)
        self._queryDF = self.getSliceDF(self._df, QueryCondition)
        self.attrParams = attrParams
        # # numerical
        # if type(self.attrParams) == list:

        self.attr = attr
        self.sensitivityWay = sensitivityWay
        self.sensitivityDF = self._df if sensitivityWay == 'Global sensitivity' else self._queryDF

    def resetParams(self, attr, QueryCondition):
        self.attr = attr
        self._queryDF = self.getSliceDF(self._df, QueryCondition)
        self.sensitivityDF = self._df if self.sensitivityWay == 'Global sensitivity' else self._queryDF

    def getSliceDF(self, df, QueryCondition):
        queryList = []
        for attr in QueryCondition.keys():
            # numerical
            if isinstance(QueryCondition[attr][0], (list, tuple)):
                # there could be multiple conditions
                temp = []  # collect first, using (join function) merge last
                for scope in QueryCondition[attr]:
                    temp.append('(({0} >= {1}) & ({0} < {2}))'.format(attr, scope[0], scope[1]))
                queryList.append('(' + '|'.join(temp) + ')')
            else:
                queryList.append('({0} in {1})'.format(attr, str(QueryCondition[attr])))
        queryStr = '&'.join(queryList)
        queryDF = df.query(queryStr) if queryStr else df
        return queryDF

    def getSumAndCountSens(self, type):
        df = self.sensitivityDF
        if type == 'numerical':
            Sensitivity = [df.max()[self.attr], 1]
        else:
            # categorical data
            Sensitivity = ['-', 1]
        return Sensitivity

    def getCurSensitivity(self, way):
        df = self.sensitivityDF
        if df.shape[0] == 0 or df.shape[0] == 1:
            return 1
        Sensitivity = 1
        if way == 'sum':
            Sensitivity = df.max(numeric_only=True)[self.attr]
        elif way == 'count':
            Sensitivity = 1
        return Sensitivity

    def getCurDataIndices(self):
        df = self.sensitivityDF
        return df.index.tolist()

    def getSensitivity(self, way):
        dfs = [self._df, self._queryDF]
        Sensitivity = []
        for df in dfs:
            if len(df) == 0:
                Sensitivity.append(1)
            elif way == 'sum':
                Sensitivity.append(df.max()[self.attr])
            elif way == 'count':
                Sensitivity.append(1)
        return Sensitivity

    def getN(self) -> Union[int, float]:
        return len(self._queryDF[self.attr])

    def sum(self) -> Union[int, float]:
        """
        Function to return total number of attr in dataset
        """
        return self._queryDF.sum()[self.attr]

    def mean(self) -> float:
        """
        Function to return mean of attr in dataset
        """
        return s.mean(list(self._queryDF[self.attr]))

    # def median(self) -> (Union[int, float], float):
    #     n = self.getN()
    #     sensitivity = 0
    #     if n % 2 == 1:
    #         a = self.percentile(((n + 1) / 2) / (n - 1))
    #         b = self.percentile(((n - 1) / 2) / (n - 1))
    #         c = self.percentile(((n - 1) / 2 - 1) / (n - 1))
    #         sensitivity = max((a - b) / 2, (b - c) / 2, (a - c))
    #     else:
    #         a = self.percentile((n / 2) / (n - 1))
    #         b = self.percentile((n / 2 - 1) / (n - 1))
    #         sensitivity = (a - b) / 2
    #     return s.median(list(self._queryDF[self.attr])), sensitivity

    def count(self) -> int:
        params = self.attrParams
        if isinstance(params, list):
            temp = self._queryDF[(self._queryDF[self.attr] > params[0]) & (self._queryDF[self.attr] < params[1])]
        else:
            temp = self._queryDF[self._queryDF[self.attr] == params]
        return temp.count()[0]

    # def max(self) -> Union[int, float]:
    #     n = self.getN()
    #     Max = self._queryDF.max()[self.attr]
    #     secondMax = self.percentile((n -1) / n)
    #     return Max, Max - secondMax
    #
    # def min(self) -> Union[int, float]:
    #     n = self.getN()
    #     Min = self._queryDF.min()[self.attr]
    #     secondMin = self.percentile(1 / n)
    #     return Min, Min - secondMin

    # def stdev(self) -> Union[int, float]:
    #     return s.pstdev(list(self._df[self.attr]))
    #
    # def variance(self) -> Union[int, float]:
    #     return s.variance(list(self._df[self.attr]))

    def percentile(self, percentile) -> float:
        return float(np.percentile(self._df[self.attr], percentile))

    # 非数值型统计计算
    def maxFrequency(self):
        utility = self._queryDF[self.attr].value_counts()
        res = utility.idxmax()
        sensitivity = 1
        return res, utility.values, sensitivity

    def maxUtilityPrice(self):
        vc = self._queryDF[self.attr]
        utility = {}
        for k in vc.value_counts().keys():
            u = len(vc[vc >= k]) * k
            utility[k] = u
        sensitivity = max(vc.value_counts().keys())
        utility = pd.Series(utility)
        res = utility.idxmax()
        return res, utility, sensitivity
