from flask import Blueprint, render_template, jsonify, url_for, redirect, request, session, flash
from flask_jwt_extended import (
	JWTManager, jwt_required, create_access_token,
	get_jwt_identity
)
import datetime, string
from database import mongo
from random import *
from functools import wraps
import os
import face_recognition
from PIL import Image

app = Blueprint('attendance', __name__,template_folder='templates')


def random_chars(y):
	return ''.join(choice(string.ascii_letters) for x in range(y))


# Check if user is admin
def is_teacher(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['type'] == 'teacher':
			return f(*args, **kwargs)
		else:
			flash('Unauthorized access, You\'re not allowed here', 'danger')
			return redirect(url_for('index'))
	return wrap

# Check if user is admin
def is_student(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if session['type'] == 'student':
			return f(*args, **kwargs)
		else:
			flash('Unauthorized access, You\'re not allowed here', 'danger')
			return redirect(url_for('index'))
	return wrap

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


@app.route('/')
@is_logged_in
@is_teacher
def index():
	x = datetime.datetime.now()
	start_time = x.strftime("%H:%M")
	end_time = int(x.strftime("%H"))+1
	time={
		'start_time':x.strftime("%H"),
		'end_time':str(int(x.strftime("%H"))+1)
	}
	date = x.strftime("%Y-%m-%d")
	all_attendances = mongo.db.attendances.find({'teacher_id':session['username']})

	return render_template('attendance.html',time=time,date=date,all_attendances = all_attendances)


@app.route('/api/', methods=['GET', 'POST'])
@jwt_required
def api():
	current_user = get_jwt_identity()
	return jsonify(logged_in_as=current_user), 200

@app.route('/api_test/', methods=['GET', 'POST'])
def api_test():

	return render_template("api_test.html")


@app.route('/create_attendance', methods=['POST'])
@is_logged_in
@is_teacher
def create_attendance():
	users = mongo.db.users
	all_students = users.find({
		'type':'student',
		'year':request.form['year'],
		'branch':request.form['branch'],
		'division':request.form['division'],
	})
	total_students = []
	for student in all_students:
		total_students.append(student['username'])

	
	attendances = mongo.db.attendances
	attendance_id = random_chars(9) + str(randint(11,99))
	attendances.insert_one({
		'id':attendance_id,
		'teacher_id':session['username'],
		'start_time':request.form['start_time'],
		'end_time':request.form['end_time'],
		'classroom':request.form['classroom'],
		'subject':request.form['subject'],
		'year':request.form['year'],
		'branch':request.form['branch'],
		'division':request.form['division'],
		'created_at':datetime.datetime.now(),
		'updated_at':datetime.datetime.now(),
		'date':request.form['date'],
		'present':[],
		'absent':total_students
	})
	
	
	return redirect(url_for('attendance.lecture',id=attendance_id,all_students = all_students))


@app.route('/lecture/<id>/', methods=['GET', 'POST'])
@is_logged_in
@is_teacher
def lecture(id):
	attendance = mongo.db.attendances.find_one({'id':id})
	users = mongo.db.users
	all_students = []

	for student_id in attendance['present']:
		s = users.find_one({'username':student_id,'approved':'yes'})
		if s:
			st = {
				'username':s['username'],
				'prn':s['prn'],
				'fname':s['fname'],
				'mname':s['mname'],
				'lname':s['lname'],
				'status':'present'
			}
			all_students.append(st)

	for student_id in attendance['absent']:
		s = users.find_one({'username':student_id,'approved':'yes'})
		if s:
			st = {
				'username':s['username'],
				'prn':s['prn'],
				'fname':s['fname'],
				'mname':s['mname'],
				'lname':s['lname'],
				'status':'absent'
			}
			all_students.append(st)

	return render_template("attendance_lecture.html",attendance=attendance,all_students = all_students)





@app.route('/change_status/<current_status>/<lecture_id>/<student_id>', methods=['GET', 'POST'])
def attendance_change_status(current_status,lecture_id,student_id):
	attendance = mongo.db.attendances
	if current_status == 'present':
		attendance.update_one({'id':lecture_id},{ '$pull': { 'present': student_id } })
		attendance.update_one({'id':lecture_id},{ '$addToSet': { 'absent': student_id } })
	else:
		attendance.update_one({'id':lecture_id},{ '$pull': { 'absent': student_id } })
		attendance.update_one({'id':lecture_id},{ '$addToSet': { 'present': student_id } })
	return redirect(url_for('attendance.lecture',id=lecture_id))







@app.route('/automatic/<lecture_id>',methods = ['POST','GET'])
@is_logged_in
@is_teacher
def automatic(lecture_id):
	attendances = mongo.db.attendances
	if session.get('unknown_face_images') is not None:
		for img in session['unknown_face_images']:
			if os.path.exists("static/unknowns/"+ session['username'] +'/'+img+".jpg"):
				os.remove("static/unknowns/"+ session['username'] +'/'+img+".jpg")
				
	if request.method == 'POST':
		x = str(datetime.datetime.now())[:10]
		path = os.path.abspath('static/attendance/'+lecture_id+'/')
		if not os.path.exists(path):
			os.makedirs(path)
		if 'image' not in request.files:
			flash('No file part')
			return redirect(request.url)
		
		file = request.files['image']
		f = os.path.join(path, file.filename)
		print(path+file.filename)
		final_path = path+'/'+file.filename
		file.save(f)
		#session['image_path'] = final_path
		#return redirect(url_for('attendance.result',lecture_id = lecture_id))

		known_count = 0
		unknown_count = 0
		known_face_encodings = []
		known_face_names = []
		unknown_face_images = []
		#vallabh_image = face_recognition.load_image_file("vallabh.jpg")
		#vallabh_face_encoding = face_recognition.face_encodings(vallabh_image)[0]
		#mangesh_image = face_recognition.load_image_file("mangesh.jpg")
		#mangesh_face_encoding = face_recognition.face_encodings(mangesh_image)[0]
#	
		#shreya_image = face_recognition.load_image_file("shreya.jpg")
		#shreya_face_encoding = face_recognition.face_encodings(shreya_image)[0]
#	
		## Create arrays of known face encodings and their names
		#known_face_encodings = [
		#    vallabh_face_encoding,
		#    mangesh_face_encoding,
		#    shreya_face_encoding
		#]
		#known_face_names = [
		#    "Vallabh Hake",
		#    "Mangesh Patil",
		#    "Shreya Wani"
		#]
	
		# with open('dataset_faces.dat', 'rb') as f:
		#    known_face_encodings = pickle.load(f)
#	
		# with open('dataset_names.dat', 'rb') as f:
		#    known_face_names = pickle.load(f)
#	
	
	
	
		train_dir = os.listdir('static/student/')
	
		# Loop through each person in the training directory
		for person in train_dir:
			if not person.startswith('.'):
				pix = os.listdir("static/student/" + person + '/train_img')
		
				# Loop through each training image for the current person
				for person_img in pix:
					# Get the face encodings for the face in each image file
					face = face_recognition.load_image_file("static/student/" + person +'/train_img/' + "/" + person_img)
					face_enc = face_recognition.face_encodings(face)[0]
		
					# Add face encoding for current image with corresponding label (name) to the training data
					known_face_encodings.append(face_enc)
					known_face_names.append(person)
	
	
	
	
		#final_path = session['image_path']
		image = face_recognition.load_image_file(final_path)
		face_locations = face_recognition.face_locations(image)
		face_encodings = face_recognition.face_encodings(image, face_locations)
		face_names = []
	
		for face_encoding, face_location in zip(face_encodings, face_locations):
				# See if the face is a match for the known face(s)
			matches = face_recognition.compare_faces(
				known_face_encodings, face_encoding, 0.5)
			name = "Unknown"
			#distance = face_recognition.face_distance(known_face_encodings, face_encoding)
	
			# If a match was found in known_face_encodings, just use the first one.
			if True in matches:
				first_match_index = matches.index(True)
				name = known_face_names[first_match_index]
				known_count = known_count+1
				attendances.update_one({'id':lecture_id},{ '$pull': { 'absent': name } })
				attendances.update_one({'id':lecture_id},{ '$addToSet': { 'present': name } })
			else:
				unknown_count = unknown_count+1
	
				top, right, bottom, left = face_location
				print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(
					top, left, bottom, right))
				face_image = image[top-100:bottom+100, left-100:right+100]
				pil_image = Image.fromarray(face_image)
				#pil_image.show()
			   
				random_name = random_chars(7)+str(randint(111,999))
				
				unknown_face_images.append(random_name)
				path = os.path.abspath('static/unknowns/'+ session['username'] + '/')
				if not os.path.exists(path):
					os.makedirs(path)
				pil_image.save('static/unknowns/'+ session['username'] + '/' + random_name + '.jpg')
	
			face_names.append(name)
	
		number_of_students = len(face_locations)
		# print(number_of_students)
		os.remove(final_path)
		session['image_path'] = ''
		session['unknown_face_images'] = unknown_face_images

		data = {
			'number_of_students':number_of_students,
			'face_names':face_names,
			'known_count':known_count,
			'unknown_count':unknown_count,
			'unknown_face_images' : unknown_face_images
		}
		print(data)
		return render_template('automatic.html',lecture_id = lecture_id , data=data)
	return render_template('automatic.html',lecture_id = lecture_id )




@app.route('/student/', methods=['GET', 'POST'])
@is_logged_in
@is_student
def attendance_student():
	users = mongo.db.users
	attendances = mongo.db.attendances.find({
		'year':session['year'],
		'branch':session['branch'],
		'division':session['division']
	})
	total_lectures = 0
	present = 0
	for a in attendances:
		if session['username'] in a['present']:
			present+=1
		total_lectures+=1

	

	data = {
		'total_lectures':total_lectures,
		'present':present,
		'absent':total_lectures - present,
		'attendance_percentage': present * 100/total_lectures
	}


	return render_template("attendance_student.html",data = data)
	






