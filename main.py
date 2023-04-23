from flask import Flask, render_template, request, url_for, redirect, jsonify, send_file
from werkzeug.utils import secure_filename
import os

from modules.database import DatabaseManager


# App setup
app = Flask(__name__)
app.config["WORKING_DIR"] = "working/"

# Database connection
db_user = "chrono-user"
db_password = "ybU62Wj58oNqTm0h"
db_manager = DatabaseManager(working_dir=app.config["WORKING_DIR"], db_addr=f"mongodb+srv://{db_user}:{db_password}@chronowave.yufcjqt.mongodb.net/?retryWrites=true&w=majority")


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

            if (file):
                file_path = os.path.join(app.config["WORKING_DIR"], file_name)
                file.save(file_path)
                db_manager.store_timeseries_set(file_path)

            return redirect(request.url)

    return render_template("upload_data.html")


@app.route("/download_data")
def download_data():
    return render_template("download_data.html")


@app.route("/view_data")
def view_data():
    return render_template("view_data.html")


@app.route("/view_history")
def view_history():
    return render_template("view_history.html")


@app.route("/performance_metrics")
def performance_metrics():
    return render_template("performance_metrics.html")


@app.route("/help")
def help():
    return render_template("help.html")


if __name__ == "__main__":
    app.run(debug=True)