from flask import Flask, render_template

app = Flask(__name__)


# Basic views
@app.route("/home")
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload_data")
def upload_data():
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