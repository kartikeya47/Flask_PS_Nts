from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/About")
def hello_user():
    return render_template("about.html")


@app.route("/Bootstrap")
def hello_boot():
    return render_template("bootstrap.html")


app.run(debug=True)
