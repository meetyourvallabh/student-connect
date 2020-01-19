from flask import Flask, render_template, redirect, request

# app = Flask(__name__,
#             static_url_path='/static',
#             static_folder='/static')

app = Flask(__name__)


@app.route("/")
def index1():
    return render_template("index.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if 0:  # check user name
            # check password
            return render_template("dashboard.html")
        else:
            # flash error
            return render_template("dashboard.html")
    else:
        return render_template("loginA.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        if 0:  # check email already present
            return render_template("register.html")
        else:
            fname = request.form['fname']
            lname = request.form['lname']
            mname = request.form['mname']
            pass1 = request.form['password']
            # create unique username
            #store in DB
            return render_template("dashboard.html")
    else:
        return render_template("register.html")


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0', debug='true', port='8080')
