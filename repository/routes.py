from flask import Blueprint, render_template, request, session
import os
import time
repo = Blueprint('repository', __name__,template_folder='templates')

def gettime(path_):
	file_token = ''
	all_time={}
	for root, dirs, files in os.walk(path_):
		for d in dirs:
			try: 
				temp = os.path.getmtime(root+"/"+d)
				all_time[d] = time.ctime(temp)
			except OSError: 
				all_time[d] = "Unknown"
		
		for f in files:
			try: 
				temp = os.path.getmtime(root+"/"+f) 
				all_time[f] = time.ctime(temp)
			except OSError: 
				all_time[f] = "Unknown"	
	return all_time

@repo.context_processor
def utility_functions():
	def print_in_console(message,txt):
		print("____========")
		print(f"value={str(message)}, txt={str(txt)}")
	return dict(mdebug=print_in_console)


@repo.route('/')
def index():
	session['main_path'] = 'static/student/mandar2'
	session['current_path'] = 'static/student/mandar2'
	
	name = "mandar"
	file_st = {}
	currentpath=[]
	dirs=[]
	files = []
	for currentpath, dirs, files in os.walk('static/student/mandar2'):
		current_dir = currentpath
		sub_dirs = dirs
		current_files = files
	
	def fs_tree_to_dict(path_):
		file_token = ''
		for root, dirs, files in os.walk(path_):
			tree = {d: fs_tree_to_dict(os.path.join(root, d)) for d in dirs}
			tree.update({f: file_token for f in files })
			for f in files:
				tree[f] = "file"
			return tree  # note we discontinue iteration trough os.walk
	tree = fs_tree_to_dict("static/student/mandar2")
	all_dirs = []
	all_files = []
	
	def find_dirs(tree):
		for k, v in tree.items():
			if isinstance(v, dict):
				all_dirs.append(k)
				find_dirs(v)
			else:
				all_files.append(k) 

	find_dirs(tree)
	all_time = gettime("static/student/mandar2")
	return render_template('repo.html',trees=tree,all_dirs=all_dirs,all_time=all_time)

def fs_tree_to_dict(path_):
	file_token = ''
	for root, dirs, files in os.walk(path_):
		tree = {d: fs_tree_to_dict(os.path.join(root, d)) for d in dirs}
		tree.update({f: file_token for f in files })
		for f in files:
			tree[f] = "file"
		return tree  


@repo.route('/next/<filepath>')
def next(filepath):
	current_path = session['current_path']
	modified_time = ''
	all_dirs = []	
	all_files = []
	
	

	def find_dirs(tree):
		for k, v in tree.items():
			if isinstance(v, dict):
				all_dirs.append(k)
				find_dirs(v)
			else:
				all_files.append(k) 

		
	all_time = gettime(session['current_path'])
	if request.method == 'GET':
		### when reloading after dir already loaded, paths are updatedm check if path already present 
		if filepath in current_path: 
			current_path = current_path.replace("/"+filepath,"")
		main_tree =  fs_tree_to_dict(current_path)
		print(f"main_tree={main_tree}")
		find_dirs(main_tree)
		if filepath in all_dirs: #display dir if dir
			current_path = current_path+'/'+filepath
			session['current_path'] = current_path
			inside_dict =  fs_tree_to_dict(current_path)
			find_dirs(inside_dict)
			return render_template('repo.html',trees=inside_dict,all_dirs=all_dirs,all_time=all_time)

		elif filepath in all_files : #display file with options
			print(f'+_+_+_+_+_+_ this is {filepath}')
			return render_template('repo.html')
		else:
			print('*******not working')
			return render_template('repo.html')

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
