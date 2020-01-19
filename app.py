from flask import Flask, render_template, redirect

# app = Flask(__name__,
#             static_url_path='/static',
#             static_folder='/static')

app = Flask(__name__)


@app.route("/")
def index1():
    return render_template("index.html")


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0', debug='true', port='8080')
