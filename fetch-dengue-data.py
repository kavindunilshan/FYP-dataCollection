import pandas as pd
import requests
import csv

filtered_cities_file = './csv/output/filtered_RJ_cities.csv'
filtered_df = pd.read_csv(filtered_cities_file)

all_data = []
header_added = False

for index, row in filtered_df.iterrows():
    city = row['name']
    geocode = row['idIBGE']

    for year in range(2012, 2023):
        url = f"https://info.dengue.mat.br/api/alertcity?geocode={geocode}&disease=dengue&format=csv&ew_start=1&ew_end=50&ey_start={year}&ey_end={year}"

        response = requests.get(url)

        if response.status_code == 200:
            decoded_content = response.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            response_df = pd.DataFrame(list(cr))
            response_df['city'] = city
            response_df['geocode'] = geocode

            if not header_added:
                header_added = True
            else:
                response_df = response_df.drop(0)

            all_data.append(response_df)

            print(f"Data retrieved for geocode {geocode} and year {year}")
        else:
            print(f"Failed to retrieve data for geocode {geocode} and year {year}")

final_df = pd.concat(all_data, ignore_index=True)
final_df.to_csv('dengue_data_filtered_RJ_2012_to_2022.csv', index=False)

print("Data has been saved to dengue_data_filtered_RJ_2012_to_2022.csv")
