# This might be used for the actual camera access page, ask kate

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


