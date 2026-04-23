from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
import csv, os
import base64
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

stripselect_bp = Blueprint("stripselect", __name__, template_folder="../templates")
os.makedirs("static/photos", exist_ok=True)
os.makedirs("data", exist_ok=True)
LOG_PATH = "data/log.csv"


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
    session["saved_photos"] = []  # clear saved photos on retake
    return render_template("camerapage.html", photo_count=count, last_button=button)


@stripselect_bp.route("/take_photos", methods=["POST"])
# function to save users photos, called by the camerapage.html script when the user takes a photo
def take_photos():

    # gets users photo,
    # need to send it here as a json object with the key "image"
    data = request.json.get("image")
    if not data:
        return "Error, no photo recieved"

    # saves the pohto to the static/photos directory
    # The filename has the users session id and the photo count to make it unique
    image_data = base64.b64decode(data.split(",")[1])

    photos_taken = session.get("photos_taken", 0) + 1
    session["photos_taken"] = photos_taken
    button = session.get("button_name", "unknown")

    filename = f"static/photos/{button}_{photos_taken}.jpg"
    with open(filename, "wb") as f:
        f.write(image_data)

    # Track saved photos in session for later retrieval
    saved = session.get("saved_photos", [])
    saved.append(filename)
    session["saved_photos"] = saved

    # tells camerapage.html how many photos have been taken and how many are left, so it can update the UI
    # and also tells it if the user is done taking photos
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
        return redirect(url_for("stripselect.stripselect"))

    photo_id = max(0, min(photo_id, len(photos) - 1))
    photo = photos[photo_id]

    button = session.get("button_name", "")

    # Decide horizontal or vertical design pages
    if button in ("onebythree", "onebyfour"):
        next_url = url_for("stripselect.stripdesignh")
    else:
        next_url = url_for("stripselect.stripdesignv")

    return render_template(
        "photo-confirmation.html",
        photo_id=photo_id,
        photos=photos,
        photo=photo,
        next_url=next_url,
    )


@stripselect_bp.route("/stripdesign/v")
def stripdesignv():
    return render_template("stripdesign(v).html")


@stripselect_bp.route("/stripdesign/h")
def stripdesignh():
    return render_template("stripdesign(h).html")


@stripselect_bp.route("/stickerpage/v")
def stickerpagev():
    return render_template("stickerpage(v).html")


@stripselect_bp.route("/stickerpage/h")
def stickerpageh():
    return render_template("stickerpage(h).html")


@stripselect_bp.route("/stripcollect")
def stripcollect():
    return render_template("stripcollect.html")


from flask import jsonify


@stripselect_bp.route("/test_pattern")
def test_pattern():
    return jsonify({"test": "Endpoint is working!"})


@stripselect_bp.route("/generate_pattern", methods=["POST"])
def generate_pattern():
    print("=== generate_pattern endpoint called ===")
    print("Request JSON:", request.json)
    try:
        data = request.json
        user_description = data.get("description", "")
        color = data.get("color", "#ffffff")
        
        if not user_description:
            return jsonify({"error": "No pattern description provided"}), 400
        
        prompt = f"""Generate JavaScript Canvas 2D API code to draw a {user_description} 
        pattern on a photo strip frame. The pattern should use color '{color}'.
        The canvas context is available as 'ctx', canvas width as 'w', height as 'h'.
        Write a loop that iterates across the canvas and draws the pattern.
        Return ONLY the JavaScript code, no explanations, no markdown formatting.
        Example format:
        for (let x = 0; x < w; x += 30) {{
          for (let y = 0; y < h; y += 30) {{
            ctx.beginPath();
            ctx.arc(x, y, 5, 0, Math.PI * 2);
            ctx.fill();
          }}
        }}"""
        
        response = client.models.generate_content(  # indented correctly now
            model="gemini-2.0-flash",
            contents=prompt
        )
        code = response.text.strip()
        
        if code.startswith("```"):
            lines = code.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            code = "\n".join(lines)
        
        return jsonify({"code": code})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stripselect_bp.route("/get_photos")
def get_photos():
    photos = session.get("saved_photos", [])
    button = session.get("button_name", "fourbyone")
    web_paths = ["/" + p for p in photos]
    return jsonify({"photos": web_paths, "button": button})


# for downloading the frame
@stripselect_bp.route("/save_strip", methods=["POST"])
def save_strip():
    data = request.json.get("image")
    if not data:
        return jsonify({"error": "No image received"}), 400
    os.makedirs("static/strips", exist_ok=True)
    image_data = base64.b64decode(data.split(",")[1])
    filename = f"static/strips/strip_{session.get('button_name', 'unknown')}.png"
    with open(filename, "wb") as f:
        f.write(image_data)
    session["strip_path"] = filename
    return jsonify({"ok": True, "redirect": url_for("stripselect.stripcollect")})


@stripselect_bp.route("/download_strip")
def download_strip():
    from flask import send_file

    strip_path = session.get("strip_path")
    if not strip_path or not os.path.exists(strip_path):
        return "No strip found", 404
    return send_file(
        strip_path, as_attachment=True, download_name="photobooth_strip.png"
    )  # this is what it saves as on users computer
