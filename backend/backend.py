from flask import Flask

app = Flask(__name__)

@app.route("/time")
def time_series():
    return {"timeseries": ["data01", "data02", "data03"]}

if __name__ == "__main__":
    app.run(debug=True)