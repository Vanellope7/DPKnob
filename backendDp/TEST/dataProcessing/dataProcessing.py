import pandas as pd

df = pd.read_csv('Personal Key Indicators of Heart Disease.csv')
AgeCategory = [
    # "65-69",
    # "60-64",
    # "70-74",
    "55-59",
    "50-54",
    # "80 or older",
    # "75-79",
    '45-49',
    # "40-44",
    # "35-39",
    # "30-34",
    # "25-29"
]
# GenHealth = [
#     "Very good",
#     "Good",
#     "Excellent",
#     "Fair",
#     # "Poor"
# ]

# Diabetic = [
#     "No",
#     # "Yes",
#     "No, borderline diabetes",
#     # "Yes (during pregnancy)"
# ]

# Race = [
#     # "White",
#     # "Hispanic",
#     # "Black",
#     # "Other",
#     "Asian",
#     # "American Indian/Alaskan Native"
# ]
keepAttr = [
    "HeartDisease",
    "BMI",
    "Smoking",
    "AlcoholDrinking",
    # "Stroke",
    "PhysicalHealth",
    "MentalHealth",
    "DiffWalking",
    "Sex",
    # "AgeCategory",
    "Race",
    # "Diabetic",
    "PhysicalActivity",
    "GenHealth",
    "SleepTime",
    # "Asthma",
    # "KidneyDisease",
    # "SkinCancer"
]
df = df[df['AgeCategory'].isin(AgeCategory)]
df = df[keepAttr]
df.rename(columns={'HeartDisease': 'Disease', 'Smoking': 'Smoker', 'AlcoholDrinking': 'Drinker',
                   'PhysicalHealth': 'PhysicalH', 'MentalHealth': 'MentalH', 'GenHealth': 'GenH',
                   'DiffWalking': 'DiffWalk', 'SleepTime': 'SleepH', 'PhysicalActivity': 'PhysicalA'
                   }, inplace=True)
print(df.shape)
# print(df[df['AgeCategory'].isin(AgeCategory) & df['GenHealth'].isin(GenHealth) & df['Diabetic'].isin(Diabetic) & df[
#     'Race'].isin(Race)].shape)

# ret = df[df['AgeCategory'].isin(AgeCategory) & df['GenHealth'].isin(GenHealth) & df['Diabetic'].isin(Diabetic) & df[
#     'Race'].isin(Race)]
# ret = ret.drop(['AgeCategory', 'GenHealth', 'Diabetic', 'Race'], axis=1)
df.to_csv('case2.csv', index=False)
