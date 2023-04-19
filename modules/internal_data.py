class TimeseriesSet:
    def __init__(self, set_name, set_description, domains,
                 keywords, contributors, reference, link,
                 timeseries):
        self.name = set_name
        self.description = set_description
        self.domains = domains
        self.keywords = keywords
        self.contributors = contributors
        self.reference = reference
        self.link = link
        self._timeseries = timeseries #Set of Timeseries instances
    
    def iter(self):
        for timeseries in self._timeseries:
            yield timeseries

class Timeseries:
    def __init__(self, timeseries_name, description, domains,
                 keywords, vector, total_datapoints, sample_period,
                 training_data, forecast_task):
        self.name = timeseries_name
        self.description = description
        self.domains = domains
        self.keywords = keywords
        self._vector = vector
        self.length = total_datapoints
        self.period = sample_period
        self._training_data = training_data
        self._forecast_task = forecast_task
    
    #Yields non-standard headers in timeseries DataFrame
    #along with units in the form (label, unit) 
    def header_iter(self):
        for header in self._vector:
            yield (header['label'], header['unit'])
    
    def training_dataframe(self):
        return self._training_data
    
    def forecast_task(self):
        return self._forecast_task

class ForecastingTask:
    def __init__(self, forecast_period, forecast_count, testing_data, test_length):
        self.period = forecast_period
        self.count = forecast_count
        self._ground_truth = testing_data
        self.test_data_length = test_length 
    
    def testing_dataframe(self):
        return self._ground_truth