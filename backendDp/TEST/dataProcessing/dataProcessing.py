import pandas as pd

df = pd.read_csv('Personal Key Indicators of Heart Disease.csv')
AgeCategory = [
    # "65-69",
    # "60-64",
    # "70-74",
    # "55-59",
    # "50-54",
    # "80 or older",
    # "75-79",
    "40-44",
    "35-39",
    "30-34",
    "25-29"
]
GenHealth = [
    "Very good",
    "Good",
    "Excellent",
    "Fair",
    # "Poor"
]

Diabetic = [
    "No",
    # "Yes",
    "No, borderline diabetes",
    # "Yes (during pregnancy)"
]

Race = [
    # "White",
    # "Hispanic",
    # "Black",
    # "Other",
    "Asian",
    # "American Indian/Alaskan Native"
]

print(df[df['AgeCategory'].isin(AgeCategory) & df['GenHealth'].isin(GenHealth) & df['Diabetic'].isin(Diabetic) & df[
    'Race'].isin(Race)].shape)

ret = df[df['AgeCategory'].isin(AgeCategory) & df['GenHealth'].isin(GenHealth) & df['Diabetic'].isin(Diabetic) & df[
    'Race'].isin(Race)]
ret = ret.drop(['AgeCategory', 'GenHealth', 'Diabetic', 'Race'], axis=1)
ret.to_csv('case2-1.csv', index=False)
