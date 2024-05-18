from flask import Flask, request, redirect, uré_for, render_template, send_form_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/health")
def health():
    return "OK"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_photo():
    if "file" not in request.files:
        return "No file"
    file = request.files['file']
    if file.filename == "":
       return "No selected"
    if file:
       description = request.form["description"]
       pathPhoto = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
       file.save(pathPhoto)
       return render_template("upload.html", filename=file.filename, description=description)

@app.route("/uploads/<filename>")
def uploaded_photo(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=5000)
