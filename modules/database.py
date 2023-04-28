import os
import json
import pymongo
import zipfile
import datetime
import pandas as pd
from modules.internal_data import *
from bson.objectid import ObjectId

_date_format = "%Y-%m-%d-%H-%M-%S"

class DatabaseManager:
    def __init__(self, working_dir, db_addr):
        self._working_dir = working_dir
        self._db_addr = db_addr
        self._client = pymongo.MongoClient(db_addr)
    
    def list_set_ids(self):
        ids = [str(id) for id in self._client.db.timeset.distinct('_id')]
        return ids
    
    def get_forecast(self, id):
        doc = self._client.db.forecasts.find_one({'_id': ObjectId(id)})
        if doc is None:
            return None

        return Forecast(doc['name'], doc['contributors'], doc['upload_time'], doc['result']) 
    
    def get_dataset(self, id):
        dataset = self._client.db.datasets.find_one({'_id': ObjectId(id)})
        if dataset is None:
            return None

        return pd.DataFrame(dataset['data'])
    
    def get_timeseries_set(self, id):
        doc = self._client.db.timeset.find_one({'_id': id})
        if doc is None:
            return None

        task = ForecastingTask(doc['task']['timeseries_id'], 
                               doc['task']['period'],
                               doc['task']['count'])

        return TimeseriesSet(str(doc['_id']), doc['description'], doc['domains'],
                             doc['keywords'], doc['contributors'], doc['reference'],
                             doc['link'], doc['timeseries'], task, doc['forecasts'],
                             doc['upload_time'], self.get_timeseries)
    
    def delete_timeseries_set(self, id):
        self._client.db.timeset.delete_one({'_id': id})
    
    def get_timeseries(self, id):
        doc = self._client.db.timeseries.find_one({'_id': ObjectId(id)})
        if doc is None:
            return None

        vector = TimeseriesDescriptor(doc['vector']['timestep_label'], doc['vector']['measure_labels'])
        training_dataset = Dataset(doc['training']['dataset_id'], doc['training']['length'], doc['sampling_period'], self.get_dataset) 

        testing_dataset = None
        if 'testing' in doc:
            testing_dataset = Dataset(doc['testing']['dataset_id'], doc['training']['length'], doc['sampling_period'], self.get_dataset)

        return Timeseries(str(doc['_id']), doc['name'], doc['description'], doc['domains'],
                          doc['keywords'], vector, training_dataset, testing_dataset)
    
    def store_forecast(self, set_id, forecast_name, contributors, forecast_result):
        doc = {
            'name': forecast_name,
            'contributors': contributors,
            'upload_time': datetime.datetime.now().strftime(_date_format),
            'result': forecast_result
        }
        id = self._client.db.forecasts.insert_one(doc).inserted_id
        self._client.db.timeset.update_one({'_id': set_id}, {'$push': {'forecasts': str(id)}})
        return id

    def store_timeseries_set(self, timeseries_zip_fname):
        #Unzip file
        with zipfile.ZipFile(timeseries_zip_fname, 'r') as file:
            file.extractall(self._working_dir)

        #Open metadata file
        metadata = None
        metadata_fname = os.path.join(self._working_dir, 'metadata.json')
        if not os.path.isfile(metadata_fname):
            raise Exception("No metadata.json file provided")

        with open(metadata_fname, 'r') as file:
            metadata = json.load(file)
        
        # Return empty
        if not self._validate(metadata):
            raise Exception("Badly formated metadata.json file")

        #Create documents and import
        set_id = self._import_timeseries_set(metadata)

        #Clear working directory
        for fname in os.listdir(self._working_dir):
            os.remove(os.path.join(self._working_dir, fname))

        return set_id
    
    def _import_timeseries_set(self, metadata):
        #First create Dataset and timeseries objects
        timeseries_ids = {} 
        for timeseries in metadata['timeseries']:
            training_fname = os.path.join(self._working_dir, timeseries['training_filename'])
            training_dataset = self._read_dataset_file(training_fname)
            training_dataset_len = len(training_dataset.index)
            training_dataset_id = self._create_dataset_from_dataframe(training_dataset)

            testing_dataset_id = None
            testing_dataset_len = None 
            if 'testing_filename' in timeseries:
                testing_fname = os.path.join(self._working_dir, timeseries['testing_filename'])
                testing_dataset = self._read_dataset_file(testing_fname)
                testing_dataset_len = len(testing_dataset.index)
                testing_dataset_id = self._create_dataset_from_dataframe(testing_dataset)
            
            timeseries_id = self._create_timeseries_document(training_dataset_id, training_dataset_len,
                                             testing_dataset_id, testing_dataset_len, timeseries)
            timeseries_ids[timeseries['name']] = timeseries_id

        #Thrid create timeseries set objects
        self._create_timeset_document(timeseries_ids, metadata)
    
    def _read_timeseries_set(self, id):
        return None
    
    def _read_dataset_file(self, fname):
        ext = fname.split(".")[-1]
        data = None
        if ext == 'csv':
            data = pd.read_csv(fname)
        elif ext == 'json':
            data = pd.read_json(fname)
        elif ext == 'xls' or ext == 'xlsx':
            data = pd.read_excel(fname)
        return data
    
    def _create_dataset_from_dataframe(self, df):
        df_doc = df.to_dict("records")
        mongo_doc = { "data": df_doc }
        id = self._client.db.datasets.insert_one(mongo_doc).inserted_id
        return id 

    def _create_timeseries_document(self, train_id, train_len, test_id, test_len, timeseries):
        mongo_doc = {
            "name": timeseries['name'],
            "description": timeseries['description'],
            "domains": timeseries['domains'],
            "keywords": timeseries['keywords'],
            "vector": timeseries['vector'],
            "sampling_period": timeseries['sampling_period'],
            "training": {
                "dataset_id": train_id,
                "length": train_len
            }
        }

        if test_id is not None:
            mongo_doc['testing'] = {
                "dataset_id": test_id,
                "length": test_len
            }
        
        id = self._client.db.timeseries.insert_one(mongo_doc).inserted_id
        return id
    
    def _create_timeset_document(self, timeseries_ids, metadata):
        timeseries = [] 
        for key in timeseries_ids:
            timeseries.append(timeseries_ids[key])

        mongo_doc = {
            "_id": metadata['name'],
            "upload_time": datetime.datetime.now().strftime(_date_format),
            "timeseries": timeseries, 
            "task": {
                "period": metadata['task']['forecast_period'],
                "count": metadata['task']['count'],
                "timeseries_id": timeseries_ids[metadata['task']['timeseries_name']]
            },
            "forecasts": [],
            "description": metadata['description'],
            "domains": metadata['domains'],
            "keywords": metadata['keywords'],
            "contributors": metadata['contributors'],
            "reference": metadata['reference'],
            "link": metadata['link']
        }

        id = self._client.db.timeset.insert_one(mongo_doc).inserted_id
        return id

    def _validate(self, metadata):
        valid = "name" in metadata and \
            "timeseries" in metadata and "task" in metadata and \
            "description" in metadata and "domains" in metadata and \
            "keywords" in metadata and "contributors" in metadata and \
            "reference" in metadata and "link" in metadata
        if not valid:
            return False
        
        #Check to see if unique
        if self._client.db.timeset.find_one({'_id': metadata["name"]}) is not None:
            return False

        valid = type(metadata["timeseries"]) is list and \
            type(metadata["task"]) is dict and type(metadata["description"]) is str and \
            type(metadata["domains"]) is list and type(metadata["keywords"]) is list and \
            type(metadata["contributors"]) is list and type(metadata["reference"]) is str and \
            type(metadata["link"]) is str
        if not valid:
            return False
        
        task_md = metadata["task"]
        valid = "forecast_period" in task_md and type(task_md["forecast_period"]) is str and \
            "count" in task_md and type(task_md["count"]) is int and "timeseries_name" in task_md and \
            type(task_md["timeseries_name"]) is str
        if not valid:
            return False
        
        for timeseries_md in metadata["timeseries"]:
            valid = "name" in timeseries_md and "description" in timeseries_md and \
                "domains" in timeseries_md and "keywords" in timeseries_md and \
                "vector" in timeseries_md and "length" in timeseries_md and \
                "sampling_period" in timeseries_md and "training_filename" in timeseries_md
            
            if not valid:
                return False
            
            train_fname = os.path.join(self._working_dir, timeseries_md["training_filename"])
            if not os.path.isfile(train_fname):
                return False
            if "testing_filename" in timeseries_md:
                test_fname = os.path.join(self._working_dir, timeseries_md["testing_filename"])
                if not os.path.isfile(test_fname):
                    return False
            
            vector_md = timeseries_md["vector"]
            valid = "timestep_label" in vector_md and "measure_labels" in vector_md 
            if not valid:
                return False
        return True



