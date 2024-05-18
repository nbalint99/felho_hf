from flask import Flask, request, redirect, url_for, render_template
from flask_pymongo import PyMongo
import os

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://mongo:27017/carspics")
mongo = PyMongo(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file in"
    file = request.files["file"]
    if file.filename == "":
        return "No file selected"
    if file:
        description = request.form["description"]
        mongo.save_file(file.filename, file)
        mongo.db.uploads.insert_one({"filename": file.filename, "description": description})
        return redirect(url_for("uploaded_file", filename=file.filename))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    upload = mongo.db.uploads.find_one_or_404({"filename": filename})
    return render_template("upload.html", filename=filename, description=upload["description"])

@app.route("/file/<filename>")
def file(filename):
    return mongo.send_file(filename)

if __name__ == "__main__":
   app.run(debug=True)
