import pandas as pd
df = pd.read_excel('Employee_Creation_Test_Cases.xlsx')
print(df.columns.tolist())
try:
    print(df.head(2).to_dict('records'))
except Exception as e:
    pass
