import pandas as pd
import numpy as np

# Create rng instance
rng = np.random.default_rng()

# Read the raw data and add custom column names
data = pd.read_csv("climate_data.csv")

# Split into train and test sets
half_idx = data.shape[0] // 2
data_train = data.iloc[:half_idx].reset_index(drop=True)
data_test = data.iloc[half_idx:].reset_index(drop=True)

# Export training data as csv, json, and excel
data_train.to_csv("csv/data_train.csv", index=False)
data_train.to_json("json/data_train.json")
data_train.to_excel("excel/data_train.xlsx", index=False)

# Export testing data as csv, json, and excel
data_test.to_csv("csv/data_test.csv", index=False)
data_test.to_json("json/data_test.json")
data_test.to_excel("excel/data_test.xlsx", index=False)

# Create random forcast data
random_forcast = data_test[["date"]]
random_forcast["meantemp"] = rng.integers(data_test["meantemp"].min(), data_test["meantemp"].max(), data_test.shape[0])
random_forcast["humidity"] = rng.integers(data_test["humidity"].min(), data_test["humidity"].max(), data_test.shape[0])
random_forcast["wind_speed"] = rng.integers(data_test["wind_speed"].min(), data_test["wind_speed"].max(), data_test.shape[0])
random_forcast["meanpressure"] = rng.integers(data_test["meanpressure"].min(), data_test["meanpressure"].max(), data_test.shape[0])

# Export random forcast data as csv, json, and excel
random_forcast.to_csv("csv/random_forcast.csv", index=False)
random_forcast.to_json("json/random_forcast.json")
random_forcast.to_excel("excel/random_forcast.xlsx", index=False)