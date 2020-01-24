from flask import Flask, render_template, redirect, request, flash, url_for, session
from flask_pymongo import PyMongo
from random import seed, randint
import bcrypt
from flask_mail import Mail, Message
from functools import wraps
from flask_simple_geoip import SimpleGeoIP

# app = Flask(__name__,
#             static_url_path='/static',
#             static_folder='/static')

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'students_connect'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/students_connect'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'developer@makeyourown.club'
app.config['MAIL_PASSWORD'] = 'myocoo@123'

mongo = PyMongo(app)
mail = Mail(app)
simple_geoip = SimpleGeoIP(app)




# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please Login First', 'secondary')
            return redirect(url_for('login'))
    return wrap



@app.route("/")
@is_logged_in
def index():
    return render_template("index.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        users = mongo.db.users
        username = request.form['username']
        password = request.form['password']
        found_user = users.find_one({ '$or': [ { 'username': username }, { 'email': username } ] })
        if found_user:  # check user name
            if bcrypt.checkpw(password.encode('utf-8'), found_user['password']):
                if found_user['type'] == 'student':
                    if found_user['verification'] == 'yes':
                        session['username'] = found_user['username']
                        session['fname'] = found_user['fname']
                        session['mname'] = found_user['mname']
                        session['lname'] = found_user['lname']
                        session['type'] = found_user['type']
                        session['email']=found_user['email']
                        session['year']=found_user['year']
                        session['branch']=found_user['branch']
                        session['branch'] = found_user['branch']
                        session['logged_in']=True

                        geoip_data = simple_geoip.get_geoip_data()
                        session['geoip_data'] = geoip_data

                        flash('Login Successfull','success')
                        return redirect(url_for('index'))
                    else:
                        flash('Your Email is not verified yet, Please Do email verification by using link provided in mail','secondary')
                        flash('Wait for the email if not recieved','warning')
                        return redirect(url_for('login'))
                else:
                    session['fname'] = founduser['fname']
                    session['mname'] = founduser['mname']
                    session['lname'] = founduser['lname']
                    session['type'] = founduser['type']
                    session['email']=founduser['email']
                    session['logged_in']=True
                    if founduser['type'] in ['hod','mentor']:
                            session['branch'] = founduser['branch']
                    flash('Login Successfull','success')
                    return redirect(url_for('index'))
            else:
                flash('Wrong Password','danger')

            return render_template("login.html",username=username)
        else:
            # flash error
            flash('No user with this username!!','danger')
            return render_template("login.html")
    else:
        return render_template("login.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    
    if request.method == 'POST':
        users = mongo.db.users
        founduser = users.find_one({'email':request.form['email']})
        verification_code = str(randint(1111,9999))
        username = (request.form['fname']+request.form['mname'][0]+request.form['lname'][0]+str(randint(11,99))).lower()
        
        if users.find_one({'username':username}) is not None:
            username = request.form['fname']+request.form['mname'][0]+request.form['lname'][0]+str(randint(11,99))


        if founduser is None:
            passw = request.form['password']
            hashpass = bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt())
            
            users.insert_one({'username':username,'fname':request.form['fname'],'password':hashpass,'verification':verification_code,'approved':'no','mname':request.form['mname'],'lname':request.form['lname'],'type':'student' ,
            'email':request.form['email'],'phone':request.form['phone'], 'branch':request.form['branch'],'year':request.form['year'],'division':request.form['division'],'prn':request.form['prn']})
            msg = Message('StudentsConnect: Account registered successfully', sender='developer@makeyourown.club', recipients=[request.form['email']])
            msg_string = '<h1>Hello ' + request.form['fname']+ request.form['lname'] + '</h1><br> You are registered sucessfully !! <br><br> Click on below link to verify your account: <br> http://localhost:5000/verify/'+verification_code+'<br> Your UserID :'+username
            msg.body = msg_string
            msg.html = msg.body
            mail.send(msg)
            flash('Account registered successfully.','success')
            flash('Please complete email verification by clicking on a  verification link sent on your mail id.','secondary')
            return redirect(url_for('login'))
        else:
            flash('User with this email id '+request.form['email']+' already exists, Login with email id.','danger')

    return render_template("register.html")


@app.route('/verify/<code>',methods = ['POST','GET'])
def verify(code):
    if request.method == 'POST' or 'GET':
        users = mongo.db.users
        user = users.find_one({'verification':code})
        if user is None:
            flash('Verification link is expired or already verified','warning')
            return redirect(url_for('login'))
        else:
            users.update({'verification':code},{'$set':{'verification':'yes'}})
            session['username'] = user['username']
            session['email'] = user['email']
            session['fname'] = user['fname']
            session['lname'] = user['lname']
            session['mname'] = user['mname']
            session['year'] = user['year']
            session['branch'] = user['branch']
            session['type'] = user['type']
            session['logged_in']=True
            session['verification'] = 'yes'
            flash('Email verification done successfully','success')
            return redirect(url_for('index'))
    return redirect(url_for('index'))




@app.route('/forgot_password',methods = ['POST','GET'])
def forgot_password():
    users = mongo.db.users
    if request.method == 'POST':
        founduser = users.find_one({'email':request.form['email']})
        if founduser:
            token=str(randint(11111,99999))
            msg = Message('StudentsConnect: Password reset link', sender='developer@makeyourown.club', recipients=[request.form['email']])
            msg_string = '<h1>Hello, ' + founduser['fname'] + '</h1><br><br> Click on below button to change your account password: <br> http://localhost:5000/changepasswordtoken/'+token
            msg.body = msg_string
            msg.html = msg.body
            mail.send(msg)
            users.update({'email':request.form['email']},{'$set':{'resetlink':token}},upsert = True)
            flash('Password reset link sent successfully','success')
        else:
            flash('No user acount found for this email','danger')
        return redirect(url_for('login'))
    return render_template("forgot_password.html")


@app.route('/changepasswordtoken/<token>',methods = ['POST','GET'])
def changepasswordtoken(token):
    users = mongo.db.users
    if request.method == 'POST':
        hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        done = users.update({'resetlink':token},{'$set':{'password':hashpass,'verification':'yes'}})
        if done:
            users.update({'resetlink':token},{'$set':{'resetlink':'inactive'}})
            flash('Password changed successfully','success')
        else:
            flash('Invalid Token','danger')
            return redirect(url_for('login'))
    else:
        validtoken = users.find_one({'resetlink':token})
        if validtoken:
            return render_template("reset_password.html",token=token)
        else:
            flash('Invalid Token','danger')
            return redirect(url_for('login'))

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.clear()
        flash('Successfully logged out','success')
        return redirect(url_for('login'))
    else:
        flash('You are not Logged in','secondary')
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0', debug='true', port='5000')
