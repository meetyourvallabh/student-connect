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
    users = mongo.db.users
    if request.method == 'POST':
        userid = request.form['userid'].strip()
        password = request.form['password'].strip()
        userPresent = users.find_one({'userid': userid})
        if userPresent:  # check user name
            # check password
            return render_template("index.html")
        else:
            # flash error
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    users = mongo.db.users
    if request.method == 'POST':
        email = request.form['email'].strip()
        userPresent = users.find_one({'email': email})
        if userPresent:  # check email already present
            # flash error already present
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

            return render_template("index.html")
    else:
        return render_template("register.html")


@app.route('/resetPassword', methods=['POST', 'GET'])
def resetPassword():
    users = mongo.db.users
    if request.method == 'POST':
        email = request.form['email'].strip()
        emailPresent = users.find_one({"email": email})
        if emailPresent:
            # send reset mail
            pass
        else:
            # flash email wrong
            pass
    else:
        return render_template("resetPassword.html")


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0', debug='true', port='8080')
