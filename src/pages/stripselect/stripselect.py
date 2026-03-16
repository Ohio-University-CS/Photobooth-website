<<<<<<< HEAD
# from flask import Flask, render_template, request
# import cv2
# import os

# app = Flask(__name__)

# # Ensure photos directory exists
# os.makedirs("static/photos", exist_ok=True)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.post("/take_photos")
# def take_photos():
#     count = int(request.form["count"])

#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         return "Camera not found", 500

#     saved_files = []

#     for i in range(count):
#         ret, frame = cap.read()
#         if not ret:
#             break

#         filename = f"photo_{i+1}.png"
#         filepath = os.path.join("static/photos", filename)
#         cv2.imwrite(filepath, frame)
#         saved_files.append(filename)

#     cap.release()

#     return f"Captured {count} photos: {', '.join(saved_files)}"
    

# if __name__ == "__main__":
#     app.run(debug=True)


=======
from flask import Flask, render_template, request, redirect, url_for, session
import csv, os

app = Flask(__name__)
app.secret_key = os.urandom(24) # makes sure the session is a random string, so that it is secure

os.makedirs("static/photos", exist_ok=True) # makes sure the photos directory exists
os.makedirs("data", exist_ok=True) # makes sure the data directory exists
LOG_PATH = "data/log.csv" # path to the log file

@app.route("/stripselect", methods=["GET"])
def stripselect():
    return render_template("stripselect.html")

@app.route("/stripselect", methods=["POST"])
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

    return redirect(url_for("camera"))

@app.route("/camera")
def camera():
    count = session.get("photo_count", 1)
    button = session.get("button_name", "unknown")

    return render_template("camerapage.html",
                           photo_count=count,
                           last_button=button)

@app.route("/take_photos", methods=["POST"])
def take_photos():
    count = session.get("photo_count", 1)
    return f"Taking {count} photos (button={session.get('button_name')})"


if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> 7ef42a8d697a80b881961beb0100069e71012e5d
