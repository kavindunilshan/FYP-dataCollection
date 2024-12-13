import pandas as pd

# Specify the fields to extract
fields = [
    "data_iniSE", "SE", "casos", "pop", "tempmin", "umidmax",
    "umidmed", "umidmin", "tempmed", "tempmax", "city", "geo_code"
]

# Read the CSV file, selecting only the specified fields
dataset_path = 'csv/input/dengue_data_filtered_RJ_2012_to_2022.csv'  # Update with the path to your file
try:
    data = pd.read_csv(dataset_path, usecols=fields)

    # Rename columns to meaningful names
    data.rename(columns={
        "data_iniSE": "date",
        "SE": "week",
        "casos": "cases",
        "pop": "population",
        "umidmax": "humidity_max",
        "umidmed": "humidity_avg",
        "umidmin": "humidity_min",
        "tempmin": "tempe_min",
        "tempmed": "temp_avg",
        "tempmax": "temp_max"
    }, inplace=True)

    # Save the filtered data to a new file (optional)
    filtered_path = 'csv/output/filtered_dengue_dataset.csv'
    data.to_csv(filtered_path, index=False)
    print(f"Filtered data with renamed columns saved to {filtered_path}")

except ValueError as e:
    print(f"Error: {e}. Ensure the specified fields exist in the CSV file.")
except FileNotFoundError:
    print(f"Error: The file {dataset_path} was not found.")
