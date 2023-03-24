# with open('Customer Personality Analysis.csv') as f:
#     s = f.read()
#     cs = s.replace('\t', ',')
#     with open('converted-Customer Personality Analysis.csv', 'w') as wf:
#         wf.write(cs)

keepAttr = ["ID", "Year_Birth", "Education", "Marital_Status", "Income",
            "Kidhome", "Teenhome", "Dt_Customer", "Recency", 'Complain']  #"MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts", "MntSweetProducts", "MntGoldProds"]
print(len(keepAttr))

import pandas as pd

df = pd.read_csv('converted-Customer Personality Analysis.csv')
df = df[keepAttr]
n = df.shape[0]
for index in range(n):
    df['Dt_Customer'].iloc[index] = 2023 - int(df['Dt_Customer'][index].split('-')[2])
    df.loc[index, 'Year_Birth'] = df['Year_Birth'][index]
    df.loc[index, 'Complain'] = 'Yes' if df['Complain'][index] == 1 else 'No'

df.rename(columns={'Dt_Customer': 'Customer_Y', 'Year_Birth': 'Birth_Y', 'Marital_Status': 'Marital_Stat'}, inplace=True)
df.to_csv('case3.csv', index=False)
