from flask import Flask, render_template, request, url_for, redirect, jsonify, send_file
from flask_pymongo import MongoClient
from bson.json_util import dumps
import json
import re



app = Flask(__name__)


client = MongoClient("mongodb+srv://geoffbe0:Password1@cluster0.vqyyuag.mongodb.net/?retryWrites=true&w=majority")

db = client.flask_db
col = db.folder1

col_results = json.loads(dumps(col.find()))
@app.route("/home")
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload_data")
def upload_data():
    return render_template("upload_data.html")

#----------------------------------Start TO MONGO routes--------------------
@app.route('/upload', methods = ['POST'])  
def upload():
    if 'file' in request.files:
        file = request.files['file']
        x = json.load(file)
        col.insert_one(x)
    return redirect('/')    
    

@app.route('/download_data/<filename>')
def file(filename):
    
    edited = str(filename).replace("'name':", "")
    edited = re.sub("[{'}]", "", edited)
    edited.strip()
    filename = json.loads(dumps(col.find_one({"name":"Test Time Series"}, {"_id": 0})))
    return filename


@app.route("/download_data", methods = ['GET'])
def filenames():
    try:

        filenames = col.find({}, {"_id": 0, "name": 1})
        filedata = col.find({}, {})
        # filenames_list = []
        # for filename in filenames:
        #     edited = str(filename).replace("'name':", "")
        #     edited = re.sub("[{'}]", "", edited)
        #     edited.strip()
        #     filenames_list.append(edited)

        return render_template('download_data.html', filenames = filenames, filedata = filedata, col = col)
    except Exception:
        return redirect('/')

#-------------------------END OF MONGO----------------------------------#

  
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