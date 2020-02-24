from flask import Blueprint, render_template

mod = Blueprint('attendance', __name__,template_folder='templates')

@mod.route('/')
def index():
	return render_template('attendance.html')


@mod.route('/automatic/')
def automatic():
	return render_template('automatic.html')