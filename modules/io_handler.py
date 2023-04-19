import os
import json
import zipfile
import pandas as pd
from internal_data import *

class IOHandler:
    def __init__(self, working_dir):
        self._working_dir = working_dir
    
    # Imports new timeseries set + forecasting task into internal data format 
    def import_timeseries_zip(self, zip_fname):
        self._unzip(zip_fname)
        metadata_fname = os.path.join(self._working_dir, "metadata.json")
        timeseries_set = self._load_dataset(metadata_fname)
        self._cleanup()

        return timeseries_set
    
    # Exports timeseries set into a zip containing CSV files
    def export_timeseries(self, timeseries_set, output_dir, file_type):
        files = []
        for timeseries in timeseries_set.iter():
            file_name = os.path.join(self._working_dir, timeseries.name + ".csv")
            files.append(file_name)
            file_data = timeseries.training_dataframe().to_csv(index=False) 
            with open(file_name, "w") as outfile:
                outfile.write(file_data)
        
        zip_name = os.path.join(output_dir, timeseries_set.name + ".zip")
        with zipfile.ZipFile(zip_name, "w") as zfile:
            for file_name in files:
                zfile.write(file_name)
        
        self._cleanup()
        return zip_name

    def _unzip(self, zip_fname):
        with zipfile.ZipFile(zip_fname, 'r') as file:
            file.extractall(self._working_dir)
    
    def _load_dataset(self, fname):
        metadata = None
        with open(fname, 'r') as file:
            metadata = json.load(file)

        #Create timeseries
        timeseries_list = []
        for t_metadata in metadata['timeseries']:
            #Read forecast task
            task_metadata = t_metadata['task']
            testing_filename = os.path.join(self._working_dir, task_metadata['test_filename'])
            testing_set = pd.read_csv(testing_filename)
            forecast_task = ForecastingTask(task_metadata['period'],
                                            task_metadata['count'],
                                            testing_set,
                                            task_metadata['test_length'])

            #Read timeseries 
            training_filename = os.path.join(self._working_dir, t_metadata['training_filename'])
            training_set = pd.read_csv(training_filename)
            timeseries = Timeseries(t_metadata['name'], t_metadata['description'],
                                    t_metadata['domains'], t_metadata['keywords'],
                                    t_metadata['vector'], t_metadata['length'],
                                    t_metadata['period'], training_set, forecast_task) 

            #Append new timeseries 
            timeseries_list.append(timeseries)

        timeseries_set = TimeseriesSet(metadata['name'], metadata['description'],
                                       metadata['domains'], metadata['keywords'],
                                       metadata['contributors'], metadata['reference'],
                                       metadata['link'], timeseries_list)

        return timeseries_set

    def _cleanup(self):
        for fname in os.listdir(self._working_dir):
            os.remove(os.path.join(self._working_dir, fname))



# Unit Test Section
def test_import():
    io_handler = IOHandler("test_files/working_dir")
    timeseries_set = io_handler.import_timeseries_zip("test_files/dataset.zip")

    # Test if timeseries set was properly read and imported
    assert timeseries_set.name == "timeseries_set_test"
    assert len(timeseries_set._timeseries) == 1

    timeseries = timeseries_set._timeseries[0]
    assert timeseries.name == "timeseries_test"
    assert len(timeseries._vector) == 1
    assert timeseries.period == "1m"
    assert isinstance(timeseries.training_dataframe(), pd.DataFrame)

    task = timeseries.forecast_task()
    assert task.period == "1m"
    assert task.count == 1
    assert task.test_data_length == 1
    assert isinstance(task.testing_dataframe(), pd.DataFrame)

    # Test if working_dir was properly cleaned
    assert len(os.listdir(io_handler._working_dir)) == 0

def test_export():
    io_handler = IOHandler("test_files/working_dir")
    io_handler._unzip("test_files/dataset.zip")
    metadata_fname = os.path.join(io_handler._working_dir, "metadata.json")
    timeseries_set = io_handler._load_dataset(metadata_fname)

    # Test if export filename is as expected
    output_dir = "test_files/output_dir"
    zip_name = io_handler.export_timeseries(timeseries_set, output_dir, "csv")
    assert os.path.basename(zip_name) == "timeseries_set_test.zip"

    # Test if exported file was actually created
    zip_exists = False
    for file_name in os.listdir(output_dir):
        zip_exists = zip_exists or (os.path.basename(zip_name) == os.path.basename(file_name))
    assert zip_exists

    # Cleanup test resources
    os.remove(os.path.join(output_dir, os.path.basename(zip_name)))
    io_handler._cleanup()

    