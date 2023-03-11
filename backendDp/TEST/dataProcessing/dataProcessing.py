import pandas as pd
df = pd.read_csv('Personal Key Indicators of Heart Disease.csv')
includeVal = [
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

print(df[df['AgeCategory'].isin(includeVal)].to_csv('25-45Age-Personal Key Indicators of Heart Disease.csv', index=False))
