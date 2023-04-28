import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_log_error
from scipy.stats import pearsonr
from database import *


class MetricsCalculator:
    def __init__(self, ts_df, forecast_df):
        self.time_s_df = time_s_df
        self.forecast_df = forecast_df

    def calculate_metrics(self):
        mae = mean_absolute_error(self.time_s_df, self.forecast_df)
        mape = mean_absolute_percentage_error(self.time_s_df, self.forecast_df)
        smape = self._calculate_smape(self.time_s_df, self.forecast_df)
        mse = mean_squared_error(self.time_s_df, self.forecast_df)
        rmse = mean_squared_error(self.time_s_df, self.forecast_df, squared=False)
        corr_coef = pearsonr(self.time_s_df, self.forecast_df)[0]
        return mae, mape, smape, mse, rmse, corr_coef

    def _calculate_smape(self, actual, predicted):
        """Calculate Symmetric Mean Absolute Percentage Error."""
        num1 = (actual + predicted).abs().sum(axis=1)
        num2 = actual.abs().sum(axis=1) + predicted.abs().sum(axis=1)
        return 2 * (num1 / num2).mean()

# Load the time series and forecast data from the database
db_manager = DatabaseManager('/path/to/working_dir', 'mongodb://localhost:27017')
time_s_df = db_manager.get_timeseries('_id').training_dataset.data
forecast_df = db_manager.get_forecast('_id').result

# Calculate the metrics
calculator = MetricsCalculator(time_s_df, forecast_df)
mae, mape, smape, mse, rmse, corr_coef = calculator.calculate_metrics()

# Create a data frame with the results
results_df = pd.DataFrame({
    'MAE': [mae],
    'MAPE': [mape],
    'SMAPE': [smape],
    'MSE': [mse],
    'RMSE': [rmse],
    'Correlation Coefficient': [corr_coef]
})

print(results_df)

