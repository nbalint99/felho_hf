from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/health")
def health():
    return "OK"

@app.route("/", methods=["GET", "POST"])
def hello_world():
    uploaded_image = None
    description = None
    if request.method == "POST":
       image = request.files["image"]
       description = request.form["description"]
       if image.filename != '':
          image_place =  './upload/image.png'
          image.save(image_place)
          uploaded_image = image_place

    return render_template('index.html', uploaded_image=uploaded_image, description=description)


if __name__ == '__main__':
   app.run(debug=True)
