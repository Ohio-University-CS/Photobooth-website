# from flask import Flask, render_template, request, redirect, url_for, session
# import csv, os

# app = Flask(__name__, template_folder=os.path.abspath("src/pages"))
# app.secret_key = os.urandom(24) # makes sure the session is a random string, so that it is secure

# os.makedirs("static/photos", exist_ok=True) # makes sure the photos directory exists
# os.makedirs("data", exist_ok=True) # makes sure the data directory exists
# LOG_PATH = "data/log.csv" # path to the log file

# @app.route("/stripselect", methods=["GET"])
# def stripselect():
#     return render_template("stripselect/stripselect.html")

# @app.route("/stripselect", methods=["POST"])
# def store_choice():
#     form = request.form
#     if not form:
#         return "No selection received", 400

#     button_name = next(iter(form.keys()))
#     count = form[button_name]

#     session["photo_count"] = int(count)
#     session["button_name"] = button_name

#     with open(LOG_PATH, "a", newline="") as f:
#         writer = csv.writer(f)
#         writer.writerow([button_name, count, request.remote_addr])

#     return redirect(url_for("camera"))

# @app.route("/camera")
# def camera():
#     count = session.get("photo_count", 1)
#     button = session.get("button_name", "unknown")

#     return render_template("camerapage/camerapage.html",
#                            photo_count=count,
#                            last_button=button)

# @app.route("/take_photos", methods=["POST"])
# def take_photos():
#     count = session.get("photo_count", 1)
#     return f"Taking {count} photos (button={session.get('button_name')})"

# @app.route("/next", methods=["POST"])
# def next_page():
#     return render_template("camerapage/camerapage.html")

# if __name__ == "__main__":
#     app.run(debug=True)