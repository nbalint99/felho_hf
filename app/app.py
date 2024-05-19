from flask import Flask, request, redirect, url_for, render_template, jsonify, send_file
from flask_pymongo import PyMongo, ObjectId
from gridfs import GridFS
from bson import ObjectId
import os
import cv2
import numpy as np

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

        config_file = "config/yolov3.cfg"
        weights_file = "config/yolov3.weights"
        class_names_file = "config/coco.names"

        with open(class_names_file, "r") as f:
            class_names = f.read().strip().split("\n")

        net = cv2.dnn.readNet(config_file, weights_file)
        image = file
        blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)

        net.setInput(blob)
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

        outs = net.forward(output_layers)

        objects = []
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

                    objects.append([x, y, w, h, confidence])

        nms = cv2.dnn.NMSBoxes(np.array(objects)[:, :4], np.array(objects)[:, 4], score_threshold=0.5, nms_threshold=0.4)

        printout = 0
        for i in nms:
            index = i[0] if isinstance(i, tuple) else i
            x, y, w, h = objects[index[:4]
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            printout += 1

        cv2.imwrite(cv2out, image)

        file_id = fs.put(cv2out, filename=file.filename, content_type=file.content_type, description = description)
        return redirect(url_for('uploads', file_id=file_id))

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
