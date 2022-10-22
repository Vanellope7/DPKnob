import os
from pathlib import Path
import statistics as s
from typing import Union

# third party
import pandas as pd

# pydp absolute
import pydp as dp

from pydp.algorithms.laplacian import (
    BoundedSum,
    BoundedMean,
    BoundedStandardDeviation,
    Count,
    Max,
    Min,
    Median,
)


# Creating a class ClassReporter
class StatisticsWithPrivacy:
    # Function to read the csv file and creating a dataframe
    def __init__(self, data_filename, epsilon):
        self.data_filename = data_filename
        self.epsilon = epsilon
        self._epsilon = epsilon
        self._privacy_budget = float(1.0)

        self._df = pd.read_csv(
            self.data_filename, sep=",", names=["animal", "carrots_eaten"]
        )

    # Function to return total number of carrots in dataset.
    def sum(self) -> int:
        return self._df.sum()[1]

    # Function to return mean of the carrots in the dataset.
    def mean(self) -> float:
        # print(list(self._df["carrots_eaten"][self._df["carrots_eaten"] <= 50]))
         return s.mean(list(self._df["carrots_eaten"]))

    # Function to calculate total number of carrots above a particular row.
    def count(self, limit: list) -> int:
        temp = self._df[self._df.carrots_eaten > limit[0]]
        return temp[limit[1] > temp.carrots_eaten].count()[0]

    # Function to calculate maximum number of carrots in the column.
    def max(self) -> int:
        return self._df.max()[1]

    def stdev(self) -> float:
        return s.pstdev(list(self._df["carrots_eaten"]))

    # Function to return the remaining privacy budget.
    def privacy_budget(self) -> float:
        return self._privacy_budget

    # Function to return the DP mean of all carrots eaten.
    def private_mean(self, privacy_budget: float) -> float:
        x = BoundedMean(
            epsilon=privacy_budget, lower_bound=0, upper_bound=100, dtype="float"
        )
        return x.quick_result(list(self._df["carrots_eaten"]))

    # Function to return the DP sum of all carrots eaten.
    def private_sum(self, privacy_budget: float) -> float:
        x = BoundedSum(
            epsilon=privacy_budget,
            delta=0,
            lower_bound=0,
            upper_bound=100,
            dtype="float",
        )
        return x.quick_result(list(self._df["carrots_eaten"]))

    # Function to return the DP count of the number of animals who ate more than "limit" carrots.
    def private_count(
        self, privacy_budget: float, limit: list
    ) -> Union[int, float]:
        x = Count(epsilon=privacy_budget, dtype="int")

        temp = self._df[self._df.carrots_eaten > limit[0]]
        final = temp[limit[1] > temp.carrots_eaten]
        return x.quick_result(
            list(final["carrots_eaten"])
        )

    # Function to return the DP maximum of the number of carrots eaten by any one animal.
    def private_max(self, privacy_budget: float) -> Union[int, float]:
        # 0 and 150 are the upper and lower limits for the search bound.
        x = Max(epsilon=privacy_budget, lower_bound=0, upper_bound=100, dtype="int")
        return x.quick_result(list(self._df["carrots_eaten"]))

    # Calculates passenger age mean applying differential privacy
    def private_stdev(self, privacy_budget: float) -> float:
        x = BoundedStandardDeviation(privacy_budget, lower_bound=0, upper_bound=100, dtype="int")
        return x.quick_result(list(self._df["carrots_eaten"]))


# # get absolute path
# path = Path(os.path.dirname(os.path.abspath(__file__)))
#
c = StatisticsWithPrivacy("animals_and_carrots.csv", 1)
# print("Mean:\t" + str(c.mean()))
# print("Private Mean:\t" + str(c.private_mean(1)))
#
# print("Sum:\t" + str(c.sum()))
# print("Private Sum:\t" + str(c.private_sum(1)))
#
print("(Count) Above 70 values:\t" + str(c.count([1, 70])))
print("private Count Above:\t" + str(c.private_count(1, [1, 70])))
#
# print("Max:\t" + str(c.max()))
# print("Private Max:\t" + str(c.private_max(1)))
#
# print("k:\t" + str(c.stdev()))
# print("Private StDev:\t" + str(c.private_stdev(1)))
