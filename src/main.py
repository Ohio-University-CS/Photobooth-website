from flask import Flask, render_template
from templates.stripselect.stripselect import stripselect_app

app = Flask(__name__)
app.register_blueprint(stripselect_app, url_prefix='/stripselect')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stripselect", methods=["GET", "POST"])
def stripselect():
    return render_template("stripselect/stripselect.html")

if __name__ == "__main__":
    app.run(debug=True)
