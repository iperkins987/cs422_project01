from flask import Flask, render_template, request, redirect


app = Flask(__name__)


@app.route("/home")
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload_data")
def upload_data():
    return render_template("upload_data.html")

#Upload route to ./templates/uploads so when we upload a file it gets stored in uploads.
@app.route('/upload', methods = ['POST'])  
def upload():
    file = request.files['file']

    file.save(f'./templates/uploads/{file.filename}')

    return redirect('/')

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