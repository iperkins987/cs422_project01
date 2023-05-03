import os
import json
import zipfile

CSV_TYPE = 'csv'
JSON_TYPE = 'json'
EXCEL_TYPE = 'xlsx'

class TimeseriesSet:
    def __init__(self, set_name, set_description, domains,
                 keywords, contributors, reference, link,
                 timeseries, forecast_task, forecast_ids,
                 upload_time, retriever):
        self.upload_time = upload_time 
        self.name = set_name
        self.description = set_description
        self.domains = domains
        self.keywords = keywords
        self.contributors = contributors
        self.reference = reference
        self.link = link
        self.timeseries = timeseries #Set of Timeseries instances
        self.task = forecast_task 
        self.forecast_ids = forecast_ids 
        self._retriever = retriever
    
    def get_forecast_ids(self):
        return self.forecast_ids
    
    def get_timeseries_list(self):
        return self.timeseries
    
    def export_to_zip(self, out_dir, out_type=CSV_TYPE):
        files = []

        forecast_info = {
            "forecast_period": self.task.period, 
            "forecast_count": self.task.count
        }

        for timeseries_id in self.timeseries:
            timeseries = self._retriever(timeseries_id)
            train_fname = os.path.join(out_dir, timeseries.name + "." + out_type)
            train_df = timeseries.training_dataset.load_dataset()

            if timeseries_id == self.task.parent_timeseries_id:
                forecast_info["relevant_timeseries"] = timeseries.name


            train_data = ""
            if out_type == CSV_TYPE:
                train_data = train_df.to_csv()
            elif out_type == JSON_TYPE:
                train_data = train_df.to_json()

            if out_type == EXCEL_TYPE:
                train_data = train_df.to_excel(train_fname)
            else:
                with open(train_fname, "w") as outfile:
                    outfile.write(train_data)
            files.append(train_fname)
        
        info_fname = os.path.join(out_dir, "forecast_info.json")
        with open(info_fname, "w") as outfile:
            json.dump(forecast_info, outfile) 
        files.append(info_fname)


        zip_fname = os.path.join(out_dir, self.name + ".zip")
        with zipfile.ZipFile(zip_fname, "w") as zfile:
            for file_name in files:
                zfile.write(file_name, os.path.basename(file_name))
        
        for file_name in files:
            os.remove(file_name)
        return zip_fname 


class Dataset:
    def __init__(self, dataset_id, length, period, retriever): 
        self.dataset_id = dataset_id
        self.length = length
        self.period = period
        self._retriever = retriever
    
    def load_dataset(self):
        if self._retriever is None:
            return None 
        return self._retriever(self.dataset_id)

class TimeseriesDescriptor:
    def __init__(self, timestep_label, measure_labels):
        self.timestep_label = timestep_label
        self.measure_labels = measure_labels 

class Timeseries:
    def __init__(self, timeseries_id, timeseries_name, description, domains,
                 keywords, vector, training_dataset, testing_dataset): 
        self.timeseries_id = timeseries_id
        self.name = timeseries_name
        self.description = description
        self.domains = domains
        self.keywords = keywords
        self.timeseries_vector = vector
        self.training_dataset = training_dataset
        self.testing_dataset = testing_dataset
    
    def get_training_metadata(self):
        return self.training_dataset
        
    def get_testing_metadata(self):
        return self.testing_dataset
        
    def get_timeseries_descriptor(self):
        return self.timeseries_vector
    
class ForecastingTask:
    def __init__(self, reference_id, forecast_period, forecast_count): 
        self.period = forecast_period
        self.count = forecast_count
        self.parent_timeseries_id = reference_id

class Forecast:
    def __init__(self, forecast_name, contributors, upload_time, results):
        self.name = forecast_name
        self.contributors = contributors
        self.upload_time = upload_time
        self.forecast_results = results 