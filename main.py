from flask import Flask, render_template, request, url_for, redirect, jsonify, send_file
from werkzeug.utils import secure_filename
import os

import matplotlib
import matplotlib.pyplot as plt

from modules.database import DatabaseManager
from modules.internal_data import *
from modules.metrics import *

# App setup
app = Flask(__name__)
app.config["WORKING_DIR"] = "working/"
app.config["ALLOWED_EXTENSIONS"] = {"zip", "json", "csv", "xlsx"}

# Database connection
db_user = "chrono-user"
db_password = "ybU62Wj58oNqTm0h"
db_manager = DatabaseManager(working_dir=app.config["WORKING_DIR"], db_addr=f"mongodb+srv://{db_user}:{db_password}@chronowave.yufcjqt.mongodb.net/?retryWrites=true&w=majority")


def allowed_file(filename):
    file_type = filename.rsplit('.', 1)[1].lower()
    valid_type = file_type in app.config["ALLOWED_EXTENSIONS"]
    return ('.' in filename) and valid_type


@app.route("/home")
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload_data", methods=["POST", "GET"])
def upload_data():

    if (request.method == "POST"):
        if (request.files):
            file = request.files["dataset"]
            file_name = secure_filename(file.filename)

            if (file and allowed_file(file.filename)):
                file_path = os.path.join(app.config["WORKING_DIR"], file_name)
                file.save(file_path)
                db_manager.store_timeseries_set(file_path)

            return redirect(request.url)

    return render_template("upload_data.html")


@app.route("/upload_forcast", methods=["POST", "GET"])
def upload_forcast():
    dataset_ids = db_manager.list_set_ids()

    if (request.method == "POST"):
        if (request.files):
            file = request.files["dataset"]
            file_name = secure_filename(file.filename)
            
            if (file and allowed_file(file.filename)):
                file_path = os.path.join(app.config["WORKING_DIR"], file_name)
                file.save(file_path)

            time_series = db_manager.get_tasked_timeseries(request.form["dataset-name"])
            data_analyzer = DataAnalyzer(time_series, file_path)
            db_manager.store_forecast(request.form["dataset-name"], request.form["forcast-name"], request.form["forcast-contributors"].split(","), data_analyzer.calculate_metrics("datetime"))

        return redirect(request.url)

    return render_template("upload_forcast.html", dataset_ids=dataset_ids)


@app.route("/download_data", methods=["POST", "GET"])
def download_data():
    dataset_ids = db_manager.list_set_ids()
    dataset_id = request.args.get("dataset_id")
    # Load metadata
    if (dataset_id):
        if (dataset_id == "default"):
            metadata = False
        else:
            ts_set = db_manager.get_timeseries_set(dataset_id)
            metadata = {
                "description" : ts_set.description,
                "domains" : ts_set.domains,
                "keywords" : ts_set.keywords,
                "contributors" : ts_set.contributors,
                "reference" : ts_set.reference,
                "link" : ts_set.link
            }

        return jsonify(metadata)

    return render_template("download_data.html", dataset_ids=dataset_ids)


@app.route("/download_as_type", methods=["POST", "GET"])
def download_type():
    file_map = {"csv" : CSV_TYPE, "excel" : EXCEL_TYPE, "json" : JSON_TYPE}
    file_type = request.args.get("file_type")
    dataset_id = request.args.get("dataset_id")

    if (file_type):
        ts_set = db_manager.get_timeseries_set(dataset_id)
        file_name = ts_set.export_to_zip(app.config["WORKING_DIR"], file_map[file_type])
        return send_file(file_name, as_attachment=True)

    return redirect(url_for("download_data"))


@app.route("/performance_metrics", methods=['GET', 'POST'])
def performance_metrics():
    dataset_ids = db_manager.list_set_ids()
    dataset_id = request.args.get("dataset_id")
    # Load metadata
    if (dataset_id):
        if (dataset_id == "default"):
            metadata = False
        else:
            ts_set = db_manager.get_timeseries_set(dataset_id)
            forecast_name = request.args.get("forecast_name")
            forecast_names = []
            forecast_ids = []
            for fc_id in ts_set.forecast_ids:
                forecast_names.append(db_manager.get_forecast(fc_id).name)
                forecast_ids.append(fc_id)
            
            #If goes through if a forecast name was selected              
            if (forecast_name) and (forecast_name != "default"):
                i = 0
                #Get the forecast id index corresponding to the forecast name:
                while (forecast_names[i] != forecast_name):
                    i += 1
                forecast = db_manager.get_forecast(forecast_ids[i])    
                metadata = {
                    "description" : ts_set.description,
                    "domains" : ts_set.domains,
                    "keywords" : ts_set.keywords,
                    "contributors" : ts_set.contributors,
                    "reference" : ts_set.reference,
                    "link" : ts_set.link,
                    "forecasts" : forecast_names,
                    "mae" : forecast.forecast_results["MAE"],
                    "mape" : forecast.forecast_results["MAPE"],
                    "smape" : forecast.forecast_results["SMAPE"],
                    "mse" : forecast.forecast_results["MSE"],
                    "rmse" : forecast.forecast_results["RMSE"]
                }
            #No forecast name is selected yet
            else:
                metadata = {
                        "description" : ts_set.description,
                        "domains" : ts_set.domains,
                        "keywords" : ts_set.keywords,
                        "contributors" : ts_set.contributors,
                        "reference" : ts_set.reference,
                        "link" : ts_set.link,
                        "forecasts" : forecast_names           
                    }
            
        return jsonify(metadata)

    return render_template("performance_metrics.html", dataset_ids=dataset_ids)


@app.route("/help")
def help():
    return render_template("help.html")


@app.route("/admin", methods = ["POST", "GET"])
def admin():
    
    if request.method == "POST":
        db_manager.delete_timeseries_set(request.form['select-dataset'])

    
    dataset_ids = db_manager.list_set_ids()
    dataset_id = request.args.get("dataset_id")
    # Load metadata
    if (dataset_id):
        if (dataset_id == "default"):
            metadata = False
        else:
            ts_set = db_manager.get_timeseries_set(dataset_id)
            metadata = {
                "description" : ts_set.description,
                "domains" : ts_set.domains,
                "keywords" : ts_set.keywords,
                "contributors" : ts_set.contributors,
                "reference" : ts_set.reference,
                "link" : ts_set.link
            }

        return jsonify(metadata)

    return render_template("admin.html", dataset_ids=dataset_ids)


if __name__ == "__main__":
    app.run(debug=True)