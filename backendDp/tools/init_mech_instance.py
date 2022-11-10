import numpy as np
from diffprivlib.mechanisms import (
    Laplace, Exponential, Gaussian
)

from tools.df_processor import DFProcessor


def initMechInstance(mech: str, params: dict):
    if mech == 'Laplace':
        return Laplace(epsilon=params['epsilon'],
                       delta=params['delta'],
                       sensitivity=params['sensitivity'])
    elif mech == 'Exponential':
        return Exponential(epsilon=params['epsilon'],
                           utility=params['utility'],
                           sensitivity=params['sensitivity'])
    elif mech == 'Gaussian':
        return Gaussian(epsilon=params['epsilon'],
                        delta=params['delta'],
                        sensitivity=params['sensitivity'])
