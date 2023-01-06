import math

import pandas as pd
from diffprivlib.mechanisms import Exponential

df = pd.read_csv('../data/{0}'.format('titanic_clean.csv'))
Title = df['Title']
sensitivity = 1000
value_count = Title.value_counts()
keys = value_count.index.tolist()
values = value_count.tolist()
p_values = list(map(lambda d: math.exp(d / sensitivity / 2), values))
Sum = sum(p_values)
p_values = list(map(lambda d: d / Sum, p_values))
print(p_values)
print(keys)
print(values)
mech = Exponential(epsilon=1, utility=values, sensitivity=sensitivity)

i = 0
for k in range(10000):
    if keys[mech.randomise()] == 'Mr':
        i += 1
print(i / 10000)