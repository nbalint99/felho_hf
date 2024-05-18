from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/health")
def health():
    return "OK"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    uploaded_image = None
    description = None
    if request.method == 'POST':
       image = request.files["image"]
       description = request.form["description"]
       if image.filename == '':
          imsge_place = "./upload/image.png"
          image.save(image_place)
          upload_image = image_place
    return render_template('index.html', uploaded_image=uploaded_image, description=description)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
