from flask import Flask, request, redirect, url_for, render_template, jsonify
from flask_pymongo import PyMongo, ObjectId
from gridfs import GridFS
from bson import ObjectId
import os

app = Flask(__name__, template_folder='templates')
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://mongo:27017/carspics")
mongo = PyMongo(app)
fs = GridFS(mongo.db)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify(status="ok")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file in"
    file = request.files["file"]
    if file.filename == "":
        return "No file selected"
    if file:
        description = request.form["description"]
        file_id = fs.put(file, filename=file.filename, content_type=file.content_type, description = description)
        return redirect(url_for('upload', file_id=file_id))

@app.route("/file/<file_id>")
def file(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(file, mimetype=file.content_type)
    except Exception as exc:
        return str(exc)

@app.route("/upload/<file_id>")
def upload(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        description = file.description
        return render_template("upload.html", filename=file.filename, description=description, file_id=file_id)
    except Exception as exc:
        return str(exc)

if __name__ == "__main__":
   app.run(host="0.0.0.0", debug=True)
