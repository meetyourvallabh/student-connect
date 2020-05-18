from flask import Blueprint, render_template, jsonify, url_for, redirect, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import datetime, string
from database import mongo
from random import *


app = Blueprint('attendance', __name__,template_folder='templates')


def random_chars(y):
    return ''.join(choice(string.ascii_letters) for x in range(y))



@app.route('/')
def index():
	x = datetime.datetime.now()
	start_time = x.strftime("%H:%M")
	end_time = int(x.strftime("%H"))+1
	time={
		'start_time':x.strftime("%H"),
		'end_time':str(int(x.strftime("%H"))+1)
	}
	date = x.strftime("%Y-%m-%d")
	return render_template('attendance.html',time=time,date=date)


@app.route('/api/', methods=['GET', 'POST'])
@jwt_required
def api():
	current_user = get_jwt_identity()
	return jsonify(logged_in_as=current_user), 200

@app.route('/api_test/', methods=['GET', 'POST'])
def api_test():

	return render_template("api_test.html")


@app.route('/create_attendance', methods=['POST'])
def create_attendance():
	attendances = mongo.db.attendances
	attendance_id = random_chars(9) + str(randint(11,99))
	attendances.insert_one({
		'id':attendance_id,
		'start_time':request.form['start_time'],
		'end_time':request.form['end_time'],
		'classroom':request.form['classroom'],
		'subject':request.form['subject'],
		'year':request.form['year'],
		'branch':request.form['branch'],
		'division':request.form['division'],
		'created_at':datetime.datetime.now(),
		'updated_at':datetime.datetime.now(),
		'date':request.form['date']
	})
	
	return redirect(url_for('attendance.lecture',id=attendance_id))


@app.route('/lecture/<id>/', methods=['GET', 'POST'])
def lecture(id):
	attendance = mongo.db.attendances.find_one({'id':id})
	return render_template("attendance_lecture.html",attendance=attendance)


@app.route('/automatic/')
def automatic():
	x = datetime.datetime.now()
	start_time = x.strftime("%H:%M")
	end_time = int(x.strftime("%H"))+1
	time={
		'start_time':x.strftime("%H"),
		'end_time':str(int(x.strftime("%H"))+1)
	}
	date = x.strftime("%Y-%m-%d")
	return render_template('automatic.html',time=time,date=date)










