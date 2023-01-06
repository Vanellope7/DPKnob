from typing import Union

import numpy as np
import pandas as pd
import statistics as s


class DFProcessor:
    def __init__(self, data_filepath, attr):
        self._df = pd.read_csv(
            'data/' + data_filepath, sep=","
        )
        self.attr = attr

    def getN(self, params = None) -> Union[int, float]:
        return len(list(self._df[self.attr]))

    def sum(self, params = None) -> (Union[int, float], float):
        """
        Function to return total number of attr in dataset
        """
        return self._df.sum()[self.attr], self.max()[0]

    def mean(self, params = None) -> (float, float):
        """
        Function to return mean of attr in dataset
        """
        return s.mean(list(self._df[self.attr])), self.max()[0] / self.getN()

    def median(self, params = None) -> (Union[int, float], float):
        n = self.getN()
        sensitivity = 0
        if n % 2 == 1:
            a = self.percentile(((n + 1) / 2) / (n - 1))
            b = self.percentile(((n - 1) / 2) / (n - 1))
            c = self.percentile(((n - 1) / 2 - 1) / (n - 1))
            sensitivity = max((a - b) / 2, (b - c) / 2, (a - c))
        else:
            a = self.percentile((n / 2) / (n - 1))
            b = self.percentile((n / 2 - 1) / (n - 1))
            sensitivity = (a - b) / 2
        return s.median(list(self._df[self.attr])), sensitivity

    def count(self, params) -> (int, int):
        temp = self._df[self._df[self.attr] > params[0]]
        return temp[params[1] > temp[self.attr]].count()[0], 1

    def max(self, params = None) -> (Union[int, float], float):
        n = self.getN()
        Max = self._df.max()[self.attr]
        secondMax = self.percentile((n -1) / n)
        return Max, Max - secondMax

    def min(self, params = None) -> (Union[int, float], float):
        n = self.getN()
        Min = self._df.min()[self.attr]
        secondMin = self.percentile(1 / n)
        return Min, Min - secondMin

    # def stdev(self) -> Union[int, float]:
    #     return s.pstdev(list(self._df[self.attr]))
    #
    # def variance(self) -> Union[int, float]:
    #     return s.variance(list(self._df[self.attr]))

    def percentile(self, percentile) -> float:
        return float(np.percentile(self._df[self.attr], percentile))

    # 非数值型统计计算
    def maxFrequency(self):
        utility = self._df[self.attr].value_counts()
        res = utility.idxmax()
        sensitivity = 1
        return res, utility.values, sensitivity

    def maxUtilityPrice(self):
        vc = self._df[self.attr]
        utility = {}
        for k in vc.value_counts().keys():
            u = len(vc[vc >= k]) * k
            utility[k] = u
        sensitivity = max(vc.value_counts().keys())
        utility = pd.Series(utility)
        res = utility.idxmax()
        return res, utility, sensitivity


