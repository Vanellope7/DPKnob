import os
from pathlib import Path
import statistics as s
from typing import Union

# third party
import numpy as np
import pandas as pd

# pydp absolute
import pydp as dp
from matplotlib import pyplot as plt

from pydp.algorithms.laplacian import (
    BoundedSum,
    BoundedMean,
    BoundedStandardDeviation,
    BoundedVariance,
    Count,
    Max,
    Min,
    Median,
    Percentile
)

# Creating a class ClassReporter
class StatisticsWithPrivacy:
    # Function to read the csv file and creating a dataframe
    def __init__(self, data_filename, attr, params):
        self.data_filename = data_filename
        self.epsilon = params['epsilon']
        self._epsilon = params['epsilon']
        self._privacy_budget = params['epsilon']
        self.params = params

        self._df = pd.read_csv(
            self.data_filename, sep=","
        )
        self.attr = attr

    # Function to return total number of carrots in dataset.
    def sum(self) -> int:
        return self._df.sum()[self.attr]

    # Function to return mean of the carrots in the dataset.
    def mean(self) -> float:
        return s.mean(list(self._df[self.attr]))

    def median(self) -> float:
        return s.median(list(self._df[self.attr]))

    # Function to calculate total number of carrots above a particular row.
    def count(self) -> int:
        limit = self.params['scope']
        temp = self._df[self._df[self.attr] > limit[0]]
        return temp[limit[1] > temp[self.attr]].count()[0]

    # Function to calculate maximum number of carrots in the column.
    def max(self) -> int:
        return self._df.max()[self.attr]

    def min(self) -> int:
        return self._df.min()[self.attr]

    def stdev(self) -> float:
        return s.pstdev(list(self._df[self.attr]))

    def variance(self) -> float:
        return s.variance(list(self._df[self.attr]))

    def percentile(self) -> int:
        return np.percentile(self._df[self.attr], self.params['percentile'])
    # Function to return the remaining privacy budget.
    def privacy_budget(self) -> float:
        return self._privacy_budget

    # Function to return the DP mean of all carrots eaten.
    def private_mean(self) -> float:
        privacy_budget = self.privacy_budget()
        x = BoundedMean(
            epsilon=privacy_budget, lower_bound=0, upper_bound=100, dtype="float"
        )
        return x.quick_result(list(self._df[self.attr]))

    # Function to return the DP sum of all carrots eaten.
    def private_sum(self) -> float:
        privacy_budget = self.privacy_budget()
        x = BoundedSum(
            epsilon=privacy_budget,
            delta=0,
            lower_bound=0,
            upper_bound=100,
            dtype="float",
        )
        return round(x.quick_result(list(self._df[self.attr])), 2)

    # Function to return the DP count of the number of animals who ate more than "limit" carrots.
    def private_count(self) -> Union[int, float]:
        limit = self.params['scope']
        privacy_budget = self.privacy_budget()
        x = Count(epsilon=privacy_budget, dtype="int")
        temp = self._df[self._df.carrots_eaten > limit[0]]
        final = temp[limit[1] > temp.carrots_eaten]
        return x.quick_result(
            list(final[self.attr])
        )

    # Function to return the DP maximum of the number of carrots eaten by any one animal.
    def private_max(self) -> Union[int, float]:
        privacy_budget = self.privacy_budget()
        x = Max(epsilon=privacy_budget, lower_bound=0, upper_bound=100, dtype="int")
        return x.quick_result(list(self._df[self.attr]))

    def private_min(self) -> Union[int, float]:
        privacy_budget = self.privacy_budget()
        x = Min(epsilon=privacy_budget, lower_bound=0, upper_bound=100, dtype="int")
        return x.quick_result(list(self._df[self.attr]))

    def private_median(self) -> Union[int, float]:
        privacy_budget = self.privacy_budget()
        x = Median(epsilon=privacy_budget, lower_bound=0, upper_bound=100, dtype="int")
        return x.quick_result(list(self._df[self.attr]))

    def private_stdev(self) -> float:
        privacy_budget = self.privacy_budget()
        x = BoundedStandardDeviation(privacy_budget, lower_bound=0, upper_bound=100, dtype="int")
        return x.quick_result(list(self._df[self.attr]))

    def private_variance(self) -> float:
        privacy_budget = self.privacy_budget()
        x = BoundedVariance(privacy_budget, lower_bound=0, upper_bound=100, dtype="int")
        return x.quick_result(list(self._df[self.attr]))

    def private_percentile(self) -> Union[int, float]:
        privacy_budget = self.privacy_budget()
        x = Percentile(privacy_budget, lower_bound=0, upper_bound=100, percentile=self.params['percentile'], dtype="int")
        return x.quick_result(list(self._df[self.attr]))

# # get absolute path
# path = Path(os.path.dirname(os.path.abspath(__file__)))
#
# c = StatisticsWithPrivacy("../data/animals_and_carrots.csv", 'carrots_eaten', {'epsilon': 0.0002, 'percentile': 0.2})
# print("Mean:\t" + str(c.mean()))
# print("Private Mean:\t" + str(c.private_mean(1)))
#
# print("Sum:\t" + str(c.sum()))
# print("Private Sum:\t" + str(c.private_sum(1)))
#
# print("(Count) Above 70 values:\t" + str(c.count([1, 70])))
# print("private Count Above:\t" + str(c.private_count(1, [1, 70])))
#
# print("Max:\t" + str(c.max()))
# print("Private Max:\t" + str(c.private_max(1)))
#
# print("k:\t" + str(c.stdev()))
# print("Private StDev:\t" + str(c.private_stdev(1)))

# print(str(c.private_percentile()))

# print(np.linspace(0, 100, 11))



