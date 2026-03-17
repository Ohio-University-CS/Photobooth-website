from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
import csv, os

stripselect_bp = Blueprint('stripselect', __name__, template_folder='../templates')
os.makedirs("static/photos", exist_ok=True) # makes sure the photos directory exists
os.makedirs("data", exist_ok=True) # makes sure the data directory exists
LOG_PATH = "data/log.csv" # path to the log file

@stripselect_bp.route("/stripselect", methods=["GET"])
def stripselect():
    return render_template("stripselect.html")

@stripselect_bp.route("/", methods=["POST"])
def store_choice():
    form = request.form
    if not form:
        return "No selection received", 400

    button_name = next(iter(form.keys()))
    count = form[button_name]

    session["photo_count"] = int(count)
    session["button_name"] = button_name

    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([button_name, count, request.remote_addr])

    return redirect(url_for("stripselect.camera"))

@stripselect_bp.route("/camera")
def camera():
    count = session.get("photo_count", 1)
    button = session.get("button_name", "unknown")

    return render_template("camerapage.html",
                           photo_count=count,
                           last_button=button)

@stripselect_bp.route("/take_photos", methods=["POST"])
def take_photos():
    count = session.get("photo_count", 1)
    return f"Taking {count} photos (button={session.get('button_name')})"

@stripselect_bp.route("/next", methods=["POST"])
def next_page():
    return render_template("camerapage.html")

