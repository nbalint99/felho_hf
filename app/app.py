from flask import Flask, request, redirect, url_for, render_template, jsonify, send_file
from flask_pymongo import PyMongo, ObjectId
from werkzeug.utils import secure_filename
from gridfs import GridFS
from bson import ObjectId
import os
import cv2
import numpy as np

app = Flask(__name__, template_folder='templates')
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://mongo:27017/carspics")
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
mongo = PyMongo(app)
fs = GridFS(mongo.db)

config_file = "config/yolov3.cfg"
weights_file = "other_config/yolov3.weights"
class_names_file = "config/coco.names"

net = cv2.dnn.readNetFromDarknet(config_file, weights_file)
with open(class_names_file, "r") as f:
    class_names = f.read().strip().split("\n")

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

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        image = cv2.imread(file_path)
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)

        net.setInput(blob)
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

        outs = net.forward(output_layers)

        objects = []
        confidences = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * image.shape[1])
                    center_y = int(detection[1] * image.shape[0])
                    w = int(detection[2] * image.shape[1])
                    h = int(detection[3] * image.shape[0])

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    objects.append([x, y, w, h])
                    confidences.append(float(confidence))

        nms = cv2.dnn.NMSBoxes(objects, confidences, score_threshold=0.5, nms_threshold=0.4)

        for i in nms:
            x, y, w, h = objects[i]
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        detect_file_path = os.path.join(app.config["UPLOAD_FOLDER"], 'detected_' + filename)
        cv2.imwrite(detect_file_path, image)

        with open(detect_file_path, "rb") as f:
            fs.put(f, filename="detected_" + filename, description=description)

        return redirect(url_for('uploads', file_id="detected_" + filename))

@app.route("/file/<file_id>")
def file(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(file, mimetype=file.content_type)
    except Exception as exc:
        return str(exc)

@app.route("/uploads/<file_id>")
def uploads(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        description = file.description
        return render_template("upload.html", filename=file.filename, description=description, file_id=file_id)
    except Exception as exc:
        return str(exc)

if __name__ == "__main__":
   app.run(host="0.0.0.0", debug=True)
