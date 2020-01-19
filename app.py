from flask import Flask, render_template, redirect, request
from flask_pymongo import PyMongo
from random import seed, randint

# app = Flask(__name__,
#             static_url_path='/static',
#             static_folder='/static')

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'studentconnect'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/studentconnect'

mongo = PyMongo(app)


@app.route("/")
def index1():
    return render_template("index.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if 0:  # check user name
            # check password
            return render_template("index.html")
        else:
            # flash error
            return render_template("dashboard.html")
    else:
        return render_template("loginA.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    users = mongo.db.users
    if request.method == 'POST':
        email = request.form['email']
        if 0:  # check email already present
            # flash error
            return render_template("register.html")
        else:
            fname = request.form['fname'].strip()
            lname = request.form['lname'].strip()
            mname = request.form['mname'].strip()
            pass1 = request.form['password'].strip()
            # bcrypt password
            # create unique username
            userid = fname+lname+str(randint(10, 999))

            #store in DB
            users.insert_one({
                'fname': fname,
                'lname': lname,
                'mname': mname,
                'email': email,
                'password': pass1,
                'userid': userid})

            return render_template("dashboard.html")
    else:
        return render_template("register.html")


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0', debug='true', port='8080')
