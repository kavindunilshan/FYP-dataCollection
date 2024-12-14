import pandas as pd
from pykrige.ok import OrdinaryKriging
import numpy as np


def filter_stations_by_availability(weather_stations, rainfall_data):
    """
    Filters weather stations based on their availability for each week.
    Args:
        weather_stations (pd.DataFrame): DataFrame with station details (id_station, record_first, record_last).
        rainfall_data (pd.DataFrame): Weekly rainfall data with `week`.
    Returns:
        pd.DataFrame: Filtered rainfall data with valid stations for each week.
    """
    # Convert date columns to datetime
    weather_stations['record_first'] = pd.to_datetime(weather_stations['record_first'])
    weather_stations['record_last'] = pd.to_datetime(weather_stations['record_last'])

    # Extract the first and last dates for each week in rainfall data
    rainfall_data['week_start'] = pd.to_datetime(rainfall_data['week'].astype(str) + '1', format='%Y%U%w')

    # Merge rainfall data with station availability
    rainfall_data = rainfall_data.merge(
        weather_stations[['id_station', 'record_first', 'record_last']],
        left_on='ESTACAO', right_on='id_station'
    )

    # Filter out stations unavailable during the week's start
    rainfall_data = rainfall_data[
        (rainfall_data['week_start'] >= rainfall_data['record_first']) &
        (rainfall_data['week_start'] <= rainfall_data['record_last'])
        ]

    # Drop unnecessary columns
    rainfall_data = rainfall_data.drop(columns=['record_first', 'record_last', 'week_start'])

    return rainfall_data


def kriging_for_cities(filtered_rainfall, cities, week_col='week', precip_col='precipitation_avg'):
    """
    Performs Kriging to predict rainfall for each city.
    Args:
        filtered_rainfall (pd.DataFrame): Filtered rainfall data (stations).
        cities (pd.DataFrame): DataFrame of cities with lat, lon, and altitude.
        week_col (str): Column representing the week.
        precip_col (str): Rainfall column to interpolate.
    Returns:
        pd.DataFrame: Predicted rainfall for each city and week.
    """
    # Initialize results
    results = []

    # Unique weeks
    weeks = filtered_rainfall[week_col].unique()

    # Iterate over each week
    for week in weeks:
        # Subset data for the week
        week_data = filtered_rainfall[filtered_rainfall[week_col] == week]

        # Extract features and target for Kriging
        station_coords = week_data[['lat', 'lon', 'lvl']].values
        rainfall_values = week_data[precip_col].values

        # Set up Kriging model
        OK = OrdinaryKriging(
            station_coords[:, 0], station_coords[:, 1], rainfall_values,
            variogram_model='spherical', verbose=False, enable_plotting=False
        )

        # Predict for all cities
        for _, city in cities.iterrows():
            predicted_rainfall, _ = OK.execute(
                'points', city['lat'], city['long']
            )
            results.append({
                'city': city['CITY'],
                'week': week,
                'predicted_precipitation_avg': predicted_rainfall
            })

    return pd.DataFrame(results)


def kriging_for_all_metrics(filtered_rainfall, cities, week_col='week'):
    """
    Predicts both average and maximum rainfall for each city.
    Args:
        filtered_rainfall (pd.DataFrame): Filtered rainfall data (stations).
        cities (pd.DataFrame): DataFrame of cities with lat, lon, and altitude.
        week_col (str): Column representing the week.
    Returns:
        pd.DataFrame: Predicted rainfall for each city and week.
    """
    # Initialize results
    results = []

    # Unique weeks
    weeks = filtered_rainfall[week_col].unique()

    # Iterate over each week
    for week in weeks:
        # Subset data for the week
        week_data = filtered_rainfall[filtered_rainfall[week_col] == week]

        # Extract features and target for Kriging
        station_coords = week_data[['lat', 'lon', 'lvl']].values
        avg_values = week_data['precipitation_avg'].values
        max_values = week_data['precipitation_max'].values

        # Set up Kriging models
        OK_avg = OrdinaryKriging(
            station_coords[:, 0], station_coords[:, 1], avg_values,
            variogram_model='spherical', verbose=False, enable_plotting=False
        )
        OK_max = OrdinaryKriging(
            station_coords[:, 0], station_coords[:, 1], max_values,
            variogram_model='spherical', verbose=False, enable_plotting=False
        )

        # Predict for all cities
        for _, city in cities.iterrows():
            predicted_avg, _ = OK_avg.execute(
                'points', city['LAT'], city['LONG']
            )
            predicted_max, _ = OK_max.execute(
                'points', city['LAT'], city['LONG']
            )
            results.append({
                'city': city['CITY'],
                'week': week,
                'predicted_precipitation_avg': predicted_avg,
                'predicted_precipitation_max': predicted_max
            })

    return pd.DataFrame(results)


def save_results_to_csv(results, filename='predicted_rainfall.csv'):
    """
    Saves the results to a CSV file.
    Args:
        results (pd.DataFrame): DataFrame of results.
        filename (str): Output file name.
    """
    results.to_csv(filename, index=False)


weather_stations = pd.read_csv('../csv/input/stations_RIO.csv')
cities = pd.read_csv('../csv/output/filtered_RJ_cities.csv')
rainfall_data = pd.read_csv('../csv/input/filtered_precipitation_data_2012_2022_by_station.csv')

# Filter stations based on availability
filtered_rainfall = filter_stations_by_availability(weather_stations, rainfall_data)

# Perform Kriging for all metrics
results = kriging_for_all_metrics(filtered_rainfall, cities)
#
# # Save results to CSV
# save_results_to_csv(results)
#
# print("Predicted rainfall data has been saved to 'predicted_rainfall.csv'.")



import pandas as pd
import numpy as np
from pykrige.ok import OrdinaryKriging

# Load the sorted data
file_path = "../krigging/data/sorted_precipitation_data.csv"
data = pd.read_csv(file_path)

# Function to perform kriging for a given city location and predict precipitation
def predict_precipitation(city_lat, city_lon, city_lvl):
    # Get unique weeks from the data
    unique_weeks = data['week'].unique()

    # Store predictions for each week
    predictions = []

    # Iterate through each week
    for week in unique_weeks:
        # Filter data for the current week
        week_data = data[data['week'] == week]

        # Prepare input arrays for kriging
        lats = week_data['lat'].values
        lons = week_data['lon'].values
        lvls = week_data['lvl'].values
        avg_precip = week_data['precipitation_avg'].values
        max_precip = week_data['precipitation_max'].values

        # Combine spatial coordinates (lat, lon, lvl) into a single array for kriging
        spatial_coords = np.column_stack((lats, lons, lvls))

        # Ordinary Kriging for precipitation_avg
        ok_avg = OrdinaryKriging(
            lats, lons, avg_precip,
            variogram_model='linear',
            verbose=False,
            enable_plotting=False
        )
        predicted_avg, _ = ok_avg.execute('points', city_lat, city_lon)

        # Ordinary Kriging for precipitation_max
        ok_max = OrdinaryKriging(
            lats, lons, max_precip,
            variogram_model='linear',
            verbose=False,
            enable_plotting=False
        )
        predicted_max, _ = ok_max.execute('points', city_lat, city_lon)

        # Append predictions for this week
        predictions.append({
            'week': week,
            'precipitation_avg': predicted_avg[0],
            'precipitation_max': predicted_max[0]
        })

    # Convert predictions to DataFrame
    prediction_df = pd.DataFrame(predictions)
    return prediction_df

# Example usage: predict precipitation for a city with given lat, lon, and lvl
city_lat = 40.0
city_lon = -75.0
city_lvl = 100.0

predictions = predict_precipitation(city_lat, city_lon, city_lvl)
print(predictions)
