from flask import Flask, send_file
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/upload')
def upload():
    return send_file('static/upload.sh')

if __name__ == "__main__":
    app.run()

