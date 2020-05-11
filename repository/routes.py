from flask import Blueprint, render_template, request, session
import os
repo = Blueprint('repository', __name__,template_folder='templates')

@repo.context_processor
def utility_functions():
	def print_in_console(message,txt):
		print("____========")
		print(f"value={str(message)}, txt={str(txt)}")
	return dict(mdebug=print_in_console)


@repo.route('/')
def index():
	name = "mandar"
	file_st = {}
	currentpath=[]
	dirs=[]
	files = []
	for currentpath, dirs, files in os.walk('static/student/mandar2'):
		current_dir = currentpath
		sub_dirs = dirs
		current_files = files
		# print(f'path={currentpath}')
		# print(f'dirs={dirs}')
		# print(f'files={files}')
		# for f in files:
			# print(f)
		# print(session['email'])
	# print(os.listdir('static/student/mandar'))
		# if currentpath 
		# file_st['current_path'] = dirs
		# file_st['sub_dirs'] = dirs
		# file_st['current_files'] = files
	
	def fs_tree_to_dict(path_):
		file_token = ''
		for root, dirs, files in os.walk(path_):
			tree = {d: fs_tree_to_dict(os.path.join(root, d)) for d in dirs}
			tree.update({f: file_token for f in files })
			for f in files:
				tree[f] = "file"
			return tree  # note we discontinue iteration trough os.walk
	tree = fs_tree_to_dict("static/student/mandar2")
	print(f"tree={tree}")
	# print(f'file_st = {file_st}')
	# print(f'tree = {tree}')
	print(type(tree))	
	all_dirs = []
	all_files = []
	# for key in tree:
	# 	print(f'key={key}')
	# 	if tree[key] != 'file':
	# 		all_dirs.append(key) 

	def find_dirs(tree):
		for k, v in tree.items():
			if isinstance(v, dict):
				all_dirs.append(k)
				find_dirs(v)
			else:
				all_files.append(k) 

	find_dirs(tree)
	print(f"all_dirs={all_dirs}")
	print(f"all_files={all_files}")
	return render_template('repo.html',trees=tree,all_dirs=all_dirs)



@repo.route('/test',methods=['POST','GET'])
def test():
	if request.method == 'GET':
		return render_template('upload.html')
	elif request.method == 'POST':
		# path = os.path.abspath('static/student/'+username)
		path = os.path.abspath('static/student/mandar')
	
		if not os.path.exists(path):
			os.makedirs(path)
			print("new path created")
		else:
			print("path already exists")

		file = request.files['file']
		f = os.path.join(path, file.filename)
		file.save(f)


		return render_template('repo.html')

@repo.route('/delete_file',methods=["POST"])
def delete_file():
	if request.method == 'POST':
		filepath = request.form['filename']
		path = os.path.abspath('static/student/mandar')
		print(path+'/'+filepath)
		print(path)
		if not os.path.exists(path+'/'+filepath):
			print("no such file")
		else:
			os.remove(path+'/'+filepath)
			print("file removed")
	return render_template('repo.html')



# path = os.path.abspath('static/student/'+username)
# app.config['UPLOAD_FOLDER'] = path
        
# file = request.files['image']
# f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
# file.save(f)
# if 'pro_pic' in user:
# 	if os.path.exists('static/'+user['pro_pic']):
# 		os.remove('static/'+user['pro_pic'])
# 	if os.path.exists('static/student/'+username+'/train_img/pro_pic.jpg'):
# 		os.remove('static/student/'+username+'/train_img/pro_pic.jpg')


# path with os.scandir, is_file etc
# with os.scandir('static/student/mandar') as entries:
#     for entry in entries:
#         print(entry.name)
