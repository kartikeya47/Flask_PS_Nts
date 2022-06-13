from flask import Flask, render_template

app = Flask(__name__)  # creating instance/object of the class Flask from the flask python package


@app.route("/")  # tells us about the route(path) in the webpage
def hello_world():
    return render_template("index.html")  # returns  the content of the webpage according to the specified route


@app.route("/About")
def hello_user():
    return render_template("about.html")


# @app.route("/user")
# def hello_user():
#     return "<p>Hello, User!</p>"


app.run(debug=True)  # this statement runs the flask web app and debug=True captures all the changes done
# automatically and implies them without rerunning the webapp
