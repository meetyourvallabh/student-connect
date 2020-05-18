from flask import Flask, render_template, redirect, request, flash, url_for, session
from database import mongo
from random import *
import bcrypt
from flask_mail import Mail, Message
from functools import wraps
import os
import datetime, string

import face_recognition
from PIL import Image
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)



# app = Flask(__name__,
#             static_url_path='/static',
#             static_folder='/static')

app = Flask(__name__)


# App configurations here!
app.config['MONGO_DBNAME'] = 'students_connect'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/students_connect'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'developer@makeyourown.club'
app.config['MAIL_PASSWORD'] = 'myocoo@123'



# App initializations here!
mail = Mail(app)
jwt = JWTManager(app) # JWT
mongo.init_app(app) # Mongo


#BLUE PRINTS
from attendance import attendance
app.register_blueprint(attendance.app,url_prefix='/attendance')




ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # for 16MB max-limit.

def random_chars(y):
    return ''.join(choice(string.ascii_letters) for x in range(y))





#MIDDLEWARES

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

# Check if user logged in
def is_already_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, **kwargs)
    return wrap



@app.route("/")
@is_logged_in
def index():
    return render_template("index.html")


@app.route("/login/", methods=['POST', 'GET'])
@is_already_logged_in
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
                        if 'pro_pic' in found_user:
                            session['pro_pic']=found_user['pro_pic']
                        session['logged_in']=True

                        

                        flash('Login Successfull','success')
                        session['access_token'] = create_access_token(identity=username,expires_delta=False)
                        return redirect(url_for('index'))
                    else:
                        flash('Your Email is not verified yet, Please Do email verification by using link provided in mail','secondary')
                        flash('Wait for the email if not recieved','warning')
                        return redirect(url_for('login'))
                else:
                    session['fname'] = found_user['fname']
                    session['mname'] = found_user['mname']
                    session['lname'] = found_user['lname']
                    session['type'] = found_user['type']
                    session['email']=found_user['email']
                    
                    if 'pro_pic' in found_user:
                            session['pro_pic']=found_user['pro_pic']

                    session['logged_in']=True
                    if found_user['type'] in ['hod','mentor']:
                            session['branch'] = found_user['branch']
                    flash('Login Successfull','success')
                    session['access_token'] = create_access_token(identity=username,expires_delta=False)
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


@app.route('/register/', methods=['POST', 'GET'])
@is_already_logged_in
def register():
    
    if request.method == 'POST':
        users = mongo.db.users
        founduser = users.find_one({'email':request.form['email']})
        verification_code = str(randint(1111,9999))
        username = (request.form['fname']+request.form['mname'][0]+request.form['lname'][0]+str(randint(11,99))).lower()
        
        username_exist = users.find_one({"username":username})
        email_exist = users.find_one({"email":request.form['email']})
        prn_exist = users.find_one({"prn":request.form['prn']})
        if email_exist: #new email already in use
            flash("Email Already exists","danger")
            return render_template("register.html")
        elif username_exist: #new username already in use
            flash("Username Already exists","danger")
            return render_template("register.html")
        elif prn_exist: #prn already in use
            flash("PRN Already exists","danger")
            return render_template("register.html")
        

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


@app.route('/verify/<code>/',methods = ['POST','GET'])
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




@app.route('/forgot_password/',methods = ['POST','GET'])
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


@app.route('/changepasswordtoken/<token>/',methods = ['POST','GET'])
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

@app.route('/logout/')
@is_logged_in
def logout():
    if 'logged_in' in session:
        session.clear()
        flash('Successfully logged out','success')
        return redirect(url_for('login'))
    else:
        flash('You are not Logged in','secondary')
        return redirect(url_for('login'))


@app.route("/profile/", methods=['POST','GET'])
@is_logged_in
def profile():
    users = mongo.db.users
    user = users.find_one({"email":session['email'], "type":"student"})

    if request.method == "POST":  
        username_exist = users.find_one({"username":request.form['username']})
        email_exist = users.find_one({"email":request.form['email']})
        prn_exist = users.find_one({"prn":request.form['prn']})
        if email_exist and user['email'] != email_exist['email']: #new email already in use
            flash("Email Already exists","danger")
            return render_template("profile.html",user=user)
        elif username_exist and user['username'] != username_exist['username']: #new username 
            flash("Username Already exists","danger")
            return render_template("profile.html",user=user)
        elif prn_exist and user['prn'] != prn_exist['prn']: #prn already used
            flash("PRN Already exists","danger")
            return render_template("profile.html",user=user)
        else:
            #update new user details
            users.update_one({"email":session['email'],"type":"student"},{"$set":{
                        "email":request.form['email'],"username":request.form['username'],
                        "fname":request.form['fname'],"lname":request.form['lname'],
                        "mname":request.form['mname'],"address":request.form['address'],
                        "phone":request.form['phone'],"branch":request.form['branch'],
                        "division":request.form['division'],"year":request.form['year'],
                        "prn":request.form['prn']
                        }},upsert=True)
            #update session
            updated_user = users.find_one({"email":request.form['email'], "type":"student"})
            session['username'] = updated_user['username']
            session['fname'] = updated_user['fname']
            session['mname'] = updated_user['mname']
            session['lname'] = updated_user['lname']
            session['type'] = updated_user['type']
            session['email']=updated_user['email']
            session['year']=updated_user['year']
            session['branch']=updated_user['branch']
            session['logged_in']=True
            flash("Profile Updated Successfully","success")
            return render_template("profile.html",user=updated_user)

    return render_template("profile.html",user=user)



@app.route("/profile_step/<step>",methods=['POST','GET'])
@is_logged_in
def profile_step(step):
    users = mongo.db.users
    user = users.find_one({'email':session['email'],"type":"student"})
    if request.method == 'POST':
        if step == "2": #settings change
            username_exist = users.find_one({"username":request.form['username']})
            if username_exist and user['username'] != username_exist['username']: #new username already exists
                flash("Username already exists","danger")
                return redirect(url_for("profile"))

            passw = request.form['password']
            if len(passw) >= 8: #password should not be empty
                hashpass = bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt())
                users.update_one({"email":session['email'],"type":"student"},{"$set":{
                    "username":request.form['username'],
                    "password":hashpass
                }})    
                session['username'] = request.form['username']
                flash("Account Updated Successfully!","success")
                return redirect(url_for("profile"))
            elif len(passw) == 0: #username change, no password change
                users.update_one({"email":session['email'],"type":"student"},{"$set":{
                    "username":request.form['username'],
                }})    
                session['username'] = request.form['username']
                flash("Account Updated Successfully!","success")
                return redirect(url_for("profile"))
            else:
                flash("Password Should be greater than 8!","danger")
                return redirect(url_for("profile"))
                
    return redirect(url_for("profile"))


@app.route('/upload_profile_image/<username>/', methods=['POST'])
def upload_profile_image(username):
    if request.method == 'POST':
        users = mongo.db.users
        user = users.find_one({'username':username})
        path = os.path.abspath('static/student/'+username)
        train_path = os.path.abspath('static/student/'+username+'/train_img')

        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(train_path):
            os.makedirs(train_path)

        app.config['UPLOAD_FOLDER'] = path
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        
        
        file = request.files['image']
        #file.seek(0, os.SEEK_END)
        #file_length = file.tell()
        #print(file_length)
        #if not file_length < 1024000 :
        #    flash('File size is greater than 1 mb','danger')
        #    return redirect(url_for('profile'))
        f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(f)

        image_file = request.files['image']
        
        pro_pic_image = face_recognition.load_image_file(image_file)
        
        face_locations = face_recognition.face_locations(pro_pic_image)
        
        if len(face_locations) > 0:
            if len(face_locations) <= 1:
                
        
                if 'pro_pic' in user:
                    if os.path.exists('static/'+user['pro_pic']):
                        os.remove('static/'+user['pro_pic'])
                    if os.path.exists('static/student/'+username+'/train_img/pro_pic.jpg'):
                        os.remove('static/student/'+username+'/train_img/pro_pic.jpg')
                
                top, right, bottom, left = face_locations[0]
                face_image = pro_pic_image[top-50:bottom+50, left-50:right+50]
                pil_image = Image.fromarray(face_image)

                random_name = random_chars(7)+str(randint(111,999))
                pil_image.save('static/student/'+username+'/train_img/pro_pic.jpg')
                #new_image = Image.fromarray(pro_pic_image)
                #new_image.save('static/student/'+username+'/pro_pic.jpg')

                
                
                
            else:
                os.remove('static/student/'+username+'/'+file.filename)
                flash('Your image contains multiple people','danger')
                return redirect(url_for('profile'))
        else:
            os.remove('static/student/'+username+'/'+file.filename)
            flash('Your image contains no faces','danger')
            return redirect(url_for('profile'))
        
        
        users.update_one({'username':username},{'$set':{'pro_pic':'student/'+username+'/'+file.filename}})
        flash('Profile Image uploaded succesfully','success')
    return redirect(url_for('profile'))







if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(host='0.0.0.0', debug='true', port='5000')
