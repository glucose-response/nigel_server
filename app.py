from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello this is the main page"

@app.route("/testing")
def testing():
    return "Hello this is a test"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)