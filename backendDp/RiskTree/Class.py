import json
import math

import numpy as np


class DataCoder:
    def __init__(self, type, params):
        self.type = type
        self.params = params

    def enCoder(self, x):
        if self.type == 'numerical':
            Min, Width = self.params['Min'], self.params['Width']
            r = (x - Min) // Width
            return r

        else:
            category_map = self.params['map']
            # 返回列表是为了与numerical返回方式统一
            return category_map[x]


class JsonEncoder(json.JSONEncoder):
    """Convert numpy classes to JSON serializable objects."""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(JsonEncoder, self).default(obj)