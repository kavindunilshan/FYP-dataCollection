import pandas as pd

file_path = './csv/input/br-city-codes.csv'
df = pd.read_csv(file_path)

filtered_df = df[df['state'] == 'RJ'][['name', 'state', 'idIBGE']]
filtered_df.to_csv('filtered_RJ_cities.csv', index=False)
