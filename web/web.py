from flask import Flask

app = Flask(__name__)

@app.route("/")
def test_out():
    return "Can you see this text? I hope so!"

if __name__ == '__main__':
   app.run(host="192.168.55.10", port=5000)
