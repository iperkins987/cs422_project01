from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo


app = Flask(__name__)

# MONGO CONNECTION:
app.config['MONGO_URI'] = 'mongodb://localhost:27017/myDatabase'
mongo = PyMongo(app)


@app.route("/home")
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload_data")
def upload_data():
    return render_template("upload_data.html")

#----------------------------------Start TO MONGO routes--------------------
#Upload route to ./templates/uploads so when we upload a file it gets stored in uploads. Records username with it.
@app.route('/upload', methods = ['POST'])  
def upload():
    if 'file' in request.files:
        file = request.files['file']
        mongo.save_file(file.filename, file)
        mongo.db.users.insert({'username': request.form.get('username'), 'file' : file.filename})
    return redirect('/')    
    

#Way to retrieve data from database
@app.route('/download_data/<filename>')
def file(filename):
    return mongo.send_file(filename)

#Displays current data in the fs.files within database
#fs.files can be swapped with whatever the collection is on the MongoDB database
@app.route("/download_data", methods = ['GET'])
def filenames():
    try:
        filenames = mongo.db.fs.files.find({})
        return render_template('download_data.html', filenames = filenames)
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