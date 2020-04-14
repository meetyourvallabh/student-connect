from flask import Blueprint, render_template, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

mod = Blueprint('attendance', __name__,template_folder='templates')




@mod.route('/')
def index():
	return render_template('attendance.html')


@mod.route('/automatic/')
def automatic():
	return render_template('automatic.html')



@mod.route('/api/', methods=['GET', 'POST'])
@jwt_required
def api():
	current_user = get_jwt_identity()
	return jsonify(logged_in_as=current_user), 200

@mod.route('/api_test/', methods=['GET', 'POST'])
def api_test():

	return render_template("api_test.html")