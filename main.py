from flask import Flask, render_template, request, url_for, redirect, jsonify, send_file, flash
from werkzeug.utils import secure_filename
import os

import matplotlib
import matplotlib.pyplot as plt

from modules.database import DatabaseManager
from modules.internal_data import *
from modules.metrics import *

# App setup
app = Flask(__name__, static_url_path="/working", static_folder="working")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["WORKING_DIR"] = "working/"
app.config["ALLOWED_EXTENSIONS"] = {"zip", "json", "csv", "xlsx"}

# Database connection
db_user = "chrono-user"
db_password = "ybU62Wj58oNqTm0h"
db_manager = DatabaseManager(working_dir=app.config["WORKING_DIR"], db_addr=f"mongodb+srv://{db_user}:{db_password}@chronowave.yufcjqt.mongodb.net/?retryWrites=true&w=majority")


# Check if a filename is one of the accepted files in app.config["ALLOWED_EXTENSIONS"]
def allowed_file(filename):
    file_type = filename.rsplit('.', 1)[1].lower()
    valid_type = file_type in app.config["ALLOWED_EXTENSIONS"]
    return ('.' in filename) and valid_type


# Render home/index page
@app.route("/home")
@app.route("/")
def home():
    return render_template("index.html")


# Render upload page and collect timeseries data
@app.route("/upload_data", methods=["POST", "GET"])
def upload_data():
    if (request.method == "POST"):
        if (request.files):
            file = request.files["dataset"]
            file_name = secure_filename(file.filename)

            if (file and allowed_file(file.filename)):
                file_path = os.path.join(app.config["WORKING_DIR"], file_name)
                file.save(file_path)

                try:
                    db_manager.store_timeseries_set(file_path)
                except Exception as e:
                    flash(str(e))

            return redirect(request.url)

    return render_template("upload_data.html")


# Render upload forcast page and collect forcast data
@app.route("/upload_forecast", methods=["POST", "GET"])
def upload_forecast():
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
            dataset_name = request.form["dataset-name"]
            forecast_name = request.form["forecast-name"]
            contributors = request.form["forecast-contributors"].split(",")
            metrics = data_analyzer.calculate_metrics()
            plot_name = data_analyzer.plot_results()

            db_manager.store_forecast(dataset_name, forecast_name, contributors, plot_name, metrics)

        return redirect(request.url)

    return render_template("upload_forecast.html", dataset_ids=dataset_ids)


# Render download page and send test data for download
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


# Download timeseries data as specified type
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


# Render performance metrics page with pre-calculated metrics
@app.route("/performance_metrics", methods=['GET', 'POST'])
def performance_metrics():
    dataset_ids = db_manager.list_set_ids()
    dataset_id = request.args.get("dataset_id")
    forecast_name = request.args.get("forecast_name")

    # Get forecast names
    if (dataset_id in dataset_ids):
        ts_set = db_manager.get_timeseries_set(dataset_id)
        forecast_ids = ts_set.get_forecast_ids()
        forecast_names = [db_manager.get_forecast(id).name for id in forecast_ids]
        forecast_lookup = dict(zip(forecast_names, forecast_ids))
        data = {"forecast_names" : forecast_names}

        # Get forecast data
        if (forecast_name in forecast_lookup):
            forecast = db_manager.get_forecast(forecast_lookup[forecast_name])
            db_manager.get_plot(forecast.plot_id, "working/graph.png")

            data["metrics"] = {
                "mae" : str(forecast.forecast_results["MAE"]),
                "mape" : str(forecast.forecast_results["MAPE"]),
                "smape" : str(forecast.forecast_results["SMAPE"]),
                "mse" : str(forecast.forecast_results["MSE"]),
                "rmse" : str(forecast.forecast_results["RMSE"]),
                "corr" : str(forecast.forecast_results["corr"]),
                "graph" : "graph.png"
            }

        return jsonify(data)

    return render_template("performance_metrics.html", dataset_ids=dataset_ids)


# Render help page
@app.route("/help")
def help():
    return render_template("help.html")


# Render admin page and delete data as requested
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