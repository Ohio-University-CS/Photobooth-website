from flask import Flask, render_template
from stripselect import stripselect_bp
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.register_blueprint(stripselect_bp, url_prefix='/stripselect')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/camerapage")
def camerapage():
    return render_template("camerapage.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
