from flask import Flask, request, redirect, url_for, render_template, jsonify, send_file, flash
from flask_pymongo import PyMongo, ObjectId
from flask_mail import Mail, Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from werkzeug.utils import secure_filename
from gridfs import GridFS
from bson import ObjectId
import os
import cv2
import numpy as np
import base64

app = Flask(__name__, template_folder='templates')
app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://mongo:27017/carspics")
app.secret_key = "xoirns-nsdnrR-4zslzt"
app.config["MAIL_USERNAME"] = "nbhofficial.drive@gmail.com"
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

secret_name = "sendgrid-api-key"
api_key_encoded = os.environ.get("SENDGRID_API_KEY")

other_mongo_client = PyMongo(app, uri=os.environ.get("OTHER_MONGO_URI", "mongodb://other-mongo:27017/email"))
other_mongo_db = other_mongo_client.db

mongo = PyMongo(app)
mail = Mail(app)
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

def send_email(recipient, subject_s, body):
    message = Mail(
        from_email=app.config["MAIL_USERNAME"],
        to_emails=recipient,
        subject=subject_s,
        html_content=body)
    try:
        sg = SendGridAPIClient(api_key_encoded)
        response = sg.send(message)
    except Exception as e:
        print(e)

def send_emails(file_url, printout):
    emails_collection = other_mongo_db.emails.find({})
    previous = fs.find()
    previous_push = [
        {
             'filename': file.filename,
             'url': url_for('uploads', filename=file.filename, _external=True)
        }
        for file in previous
    ]

    for email_doc in emails_collection:
        recipient_email = email_doc["email"]
        subject_s = "New image - auto detection"
        body = "A new image has been uploaded with {} cars, you can check it here: {}.\n\n".format(printout, file_url)

        for prev in previous_push:
            body += "{}\n".format(prev["url"])

        if send_email(recipient_email, subject_s, body):
            flash("Email siker", "success")
        else:
            flash("Hiba", "error")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file in requested"
    file = request.files["file"]
    if file.filename == "":
        return "No file selected, but it was required"
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

        printout = 0
        for i in nms:
            x, y, w, h = objects[i]
            printout += 1
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        detect_file_path = os.path.join(app.config["UPLOAD_FOLDER"], 'detected_' + filename)
        cv2.imwrite(detect_file_path, image)

        with open(detect_file_path, "rb") as f:
            fs.put(f, filename="detected_" + filename, description=description)

        file_url = url_for("uploads", filename="detected_" + filename, _external=True)
        send_emails(file_url, printout)

        return redirect(url_for('uploads', filename="detected_" + filename))

@app.route("/file/<filename>")
def file(filename):
    try:
        file = fs.find_one({"filename": filename})
        return send_file(file, mimetype=file.content_type, download_name=filename)
    except Exception as exc:
        return str(exc)

@app.route("/uploads/<filename>")
def uploads(filename):
    try:
        file = fs.find_one({"filename": filename})
        description = file.description
        return render_template("upload.html", filename=file.filename, description=description, file_id=filename)
    except Exception as exc:
        return str(exc)

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form["email"]

    if email:
       result = other_mongo_db.emails.insert_one({"email": email})
       if result.acknowledged:
           flash("Subscribe is successful!", "success")
       else:
           flash("Failed!", "error")
    else:
       flash("Email is required", "error")

    return redirect(url_for("admin"))

if __name__ == "__main__":
   app.run(host="0.0.0.0", debug=True)
