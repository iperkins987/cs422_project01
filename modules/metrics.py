import pandas as pd
import numpy as np
import json
import openpyxl
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_log_error
from typing import Dict, Union
from modules.database import *
import matplotlib.pyplot as plt


# DataAnalyzer method
class DataAnalyzer:
    # Initializa the class with a file path
    def __init__(self, time_series: Timeseries, file_path: str):
        self.time_series = time_series
        self.file_path = file_path

    # Read the file a return a DataFrame
    def read_data(self) -> pd.DataFrame:
        # Get the file extension by splitting by the point
        file_type = self.file_path.rsplit('.', 1)[1].lower()
        
        # Check for file type and process as necessary
        if file_type == 'json':
            with open(self.file_path) as file:
                data = json.load(file)
            df = pd.json_normalize(data)
            
        elif file_type == 'csv':
            df = pd.read_csv(self.file_path)
            
        elif file_type == 'xlsx':
            wb = openpyxl.load_workbook(self.file_path)
            sheet = wb.active
            rows = sheet.values
            columns = next(rows)
            df = pd.DataFrame(rows, columns=columns)
            
        return df

    #  Calculate the performance metrics and return them as a dictionary.        
    def calculate_metrics(self) -> Dict[str, Union[float, np.ndarray]]:
        index_col = self.time_series.get_timeseries_descriptor().timestep_label

        actual = self.time_series.get_testing_metadata().load_dataset()
        predicted = self.read_data()

        if (actual.shape[0] > predicted.shape[0]):
            actual = actual[actual[index_col].isin(predicted[index_col])]

        elif (actual.shape[0] < predicted.shape[0]):
            predicted = predicted[predicted[index_col].isin(actual[index_col])]

        actual = actual.drop(columns=index_col)
        predicted = predicted.drop(columns=index_col)

        mae = mean_absolute_error(actual, predicted)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        smape = 2 * np.mean(np.abs(predicted - actual) / (np.abs(actual) + np.abs(predicted))) * 100
        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
    
        # Calculating the correlation coefficient
        # Check if the actual and predicted datasets are empty, have null values, or has only 1 element. If they are then return NaN
        if len(actual) > 1 and len(predicted) > 1:
            corr = np.corrcoef(np.array(actual).flatten(), np.array(predicted).flatten())[0, 1]
        else:
            corr = np.nan
        
        return {"MAE": mae, "MAPE": mape, "SMAPE": smape, "MSE": mse, "RMSE": rmse, "Correlation Coefficient": corr}
        # return {"MAE": mae, "MAPE": mape, "SMAPE": smape, "MSE": mse, "RMSE": rmse}

    # Plotting results
    def plot_results(self, actual_col: str, predicted_col: str) -> None:
        df = self.read_data()
        actual = df[actual_col].values
        predicted = df[predicted_col].values
        
        # Scatter plot of actual vs predicted values
        plt.scatter(actual, predicted, alpha=0.5)

        # Add line representing perfect predictions
        plt.plot(np.linspace(np.min(actual), np.max(actual)), np.linspace(np.min(actual), np.max(actual)), c='r')
        
        # Add labels and title
        plt.xlabel("Actual Values")
        plt.ylabel("Predicted Values")
        plt.title("Actual vs Predicted Values")

        # Show plot
        plt.show()
