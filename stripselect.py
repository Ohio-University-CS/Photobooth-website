from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
import csv, os
import base64 # for decoding the base64 image data sent from the client


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
    session["photos_taken"] = 0  # reset every time camera page loads

    return render_template("camerapage.html",
                           photo_count=count,
                           last_button=button)

@stripselect_bp.route("/take_photos", methods=["POST"])
#function to save users photos, called by the camerapage.html script when the user takes a photo
def take_photos():

    #gets users photo, 
    #need to send it here as a json object with the key "image"
    data = request.json.get("image")
    if not data:
        return "Error, no photo recieved"
    
    #saves the pohto to the static/photos directory
    #The filename has the users session id and the photo count to make it unique
    image_data = base64.b64decode(data.split(",")[1])

    photos_taken = session.get("photos_taken", 0) + 1
    session["photos_taken"] = photos_taken
    button = session.get("button_name", "unknown")

    filename = f"static/photos/{button}_{photos_taken}.jpg"
    with open(filename, "wb") as f:
        f.write(image_data)

    saved = session.get("saved_photos", [])
    saved.append(filename)
    session["saved_photos"] = saved
    #tells camerapage.html how many photos have been taken and how many are left, so it can update the UI
    #and also tells it if the user is done taking photos
    count = session.get("photo_count", 1)
    done = photos_taken >= count
    return {"done": done, "photos_taken": photos_taken, "photo_count": count}

@stripselect_bp.route("/next", methods=["POST"])
def next_page():
    return render_template("camerapage.html")

@stripselect_bp.route("/photo-confirmation/<int:photo_id>")
def photo_confirmation(photo_id):
    photos = session.get("saved_photos", [])
    if not photos:
        return redirect(url_for("stripselect.stripselect"))  # Redirect to the stripselect page if no photos
    photo_id = max(0, min(photo_id, len(photos) - 1))  # Ensure photo_id is within bounds
    photo = photos[photo_id] 
    return render_template("photo-confirmation.html", photo_id=photo_id, photos=photos, photo=photo)

@stripselect_bp.route("/stripdesign")
def stripdesign():
    return render_template("stripdesign.html")

