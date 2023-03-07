import os
from pathlib import Path
import statistics as s
from typing import Union

# third party
import numpy as np
import pandas as pd

from tools.df_processor import DFProcessor
from tools.init_mech_instance import initMechInstance


class StatisticsWithPrivacy:
    """
    chararray(data_filepath, attr, params)

    StatisticsWithPrivacy类 用于计算真实的统计值和使用差分隐私的统计值

    Parameters
    --------
    data_filepath : string 
        filepath of the file to be statistical query
    attr : string
        attribution of the file
    params : Map
        additional params of the query way
        For example, scope for count
    """
def numericalStatistic(mech, params):
    dfp = DFProcessor(params['datafile']['filename'], params['datafile']['attr'])
    res, sensitivity = eval("dfp.{0}(params['mechParams']['scope'])".format(params['queryWay']))
    params['mechParams']['sensitivity'] = sensitivity
    return float(res), round(initMechInstance(mech, params['mechParams']).randomise(res), 4), sensitivity


def nonNumericalStatistic(mech, params):
    dfp = DFProcessor(params['datafile']['filename'], params['datafile']['attr'])
    res, utility, sensitivity = eval('dfp.{0}()'.format(params['queryWay']))
    params['mechParams']['sensitivity'] = sensitivity
    params['mechParams']['utility'] = list(utility.values)
    print(list(utility.values))
    index = initMechInstance(mech, params['mechParams']).randomise()
    print(index, utility.keys())
    return int(res), int(utility.keys()[index])







