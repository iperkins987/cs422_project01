import pandas as pd
import numpy as np
import json
import openpyxl
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_log_error
from typing import Dict, Union
from modules.database import *
from main import *
import matplotlib.pyplot as plt


# Determine the type of file we are allowing to read
def allowed_file(filename):
    file_type = filename.rsplit('.', 1)[1].lower()
    valid_type = file_type in {"zip", "json", "csv", "xlsx"}
    return ('.' in filename) and valid_type

# DataAnalyzer method
class DataAnalyzer:
    # Initializa the class with a file path
    def __init__(self, file_path: str):
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
    def calculate_metrics(self, actual_col: str, predicted_col: str) -> Dict[str, Union[float, np.ndarray]]:
        df = self.read_data()
        actual = df[actual_col].values
        predicted = df[predicted_col].values
        
        mae = mean_absolute_error(actual, predicted)
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        smape = 2 * np.mean(np.abs(predicted - actual) / (np.abs(actual) + np.abs(predicted))) * 100
        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
        corr_coef, _ = pearsonr(actual, predicted)
        
        return {"MAE": mae, "MAPE": mape, "SMAPE": smape, "MSE": mse, "RMSE": rmse, "Correlation Coefficient": corr_coef}

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
