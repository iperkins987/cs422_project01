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
    def calculate_metrics(self, index_col: str) -> Dict[str, Union[float, np.ndarray]]:
        actual = self.time_series.get_testing_metadata().load_dataset().drop(columns=index_col)
        predicted = self.read_data().drop(columns=index_col)
        
        mae = mean_absolute_error(actual, predicted)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        smape = 2 * np.mean(np.abs(predicted - actual) / (np.abs(actual) + np.abs(predicted))) * 100
        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
    
        # Calculating the correlation coefficient
        # We use the formula for population covariance np.cov() and standard deviation np.std
        # actual.T and predicted.T are the transpose of the original arrays
        # ddof means degrees of freedom meaning that the calculation should assume that the two arrays being passed in (actual and predicted) 
            # represent the entire population, rather than a sample of the population. In this case, there is no sample population
        cov = np.cov(actual.T, predicted.T, ddof=0)[0][1]
        std_actual = np.std(actual, ddof=0)
        std_predicted = np.std(predicted, ddof=0)
        corr_coeff = cov / (std_actual * std_predicted)
        
        return {"MAE": mae, "MAPE": mape, "SMAPE": smape, "MSE": mse, "RMSE": rmse, "CORRELATION COEFFICIENT": corr_coeff}

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
