from flask import Flask, render_template, request, url_for, redirect, jsonify, send_file
from werkzeug.utils import secure_filename
import os

import matplotlib
import matplotlib.pyplot as plt

from modules.database import DatabaseManager
from modules.internal_data import *

# App setup
app = Flask(__name__)
app.config["WORKING_DIR"] = "working/"
app.config["ALLOWED_EXTENSIONS"] = {"zip"}

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


@app.route("/view_data")
def view_data():
    return render_template("view_data.html")


@app.route("/view_history")
def view_history():
    return render_template("view_history.html")


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
            metadata = {
                "description" : ts_set.description,
                "domains" : ts_set.domains,
                "keywords" : ts_set.keywords,
                "contributors" : ts_set.contributors,
                "reference" : ts_set.reference,
                "link" : ts_set.link
            }

        return jsonify(metadata)

    return render_template("performance_metrics.html", dataset_ids=dataset_ids)

@app.route("/help")
def help():
    return render_template("help.html")


if __name__ == "__main__":
    app.run(debug=True)