import pandas as pd
import numpy as np

# Create rng instance
rng = np.random.default_rng()

# Read the raw data and add custom column names
data = pd.read_csv("data-55", sep="\t", names=["date", "time", "code", "value"])

# Add a date time column
date_time = pd.to_datetime(data["date"] + " " + data["time"])
data["date_time"] = date_time

# Drop old data and time columns
data.drop(columns=["date", "time"], inplace=True)

# Reorder columns
data = data[["date_time", "code", "value"]]

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
codes = data_test["code"].unique()
random_forcast = data_test[["date_time"]]
random_forcast["code"] = rng.choice(codes, data_test.shape[0])
random_forcast["value"] = rng.integers(data_test["value"].min(), data_test["value"].max(), data_test.shape[0])

# Export random forcast data as csv, json, and excel
random_forcast.to_csv("csv/random_forcast.csv", index=False)
random_forcast.to_json("json/random_forcast.json")
random_forcast.to_excel("excel/random_forcast.xlsx", index=False)