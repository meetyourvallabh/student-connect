from flask import Blueprint, render_template, request, session, redirect, url_for, send_file
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


def fs_tree_to_dict(path_):
	file_token = ''
	for root, dirs, files in os.walk(path_):
		tree = {d: fs_tree_to_dict(os.path.join(root, d)) for d in dirs}
		tree.update({f: file_token for f in files })
		for f in files:
			tree[f] = "file"
		return tree  


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
	main_tree = fs_tree_to_dict(session['main_path'])
	return render_template('repo.html',trees=tree,all_dirs=all_dirs,all_time=all_time,main_tree=main_tree)



@repo.route('/next/<filepath>')
def next(filepath):
	current_path = session['current_path']
	modified_time = ''
	all_dirs = []	
	all_files = []
	
	# print(f"file--------------------{filepath}")
	print(f"session--------------------{current_path}")

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
		reloaded = False
		if filepath in current_path:
			print(f"filepath={filepath}")
			# last_slash = current_path.rindex("/")
			# last_slash = current_path[last_slash:]
			# print(f"lasst_slash={last_slash}")
			# if filepath in last_slash:
			# 	reloaded = False
			# else:
			# 	reloaded = True
			# print(f"------reloaded={reloaded}")
			# current_path = current_path.replace("/"+filepath,"")
			##last_pos = current_path.rindex(filepath)
			# print(f"index={last_pos}")
			# current_path = current_path[:last_pos+len(filepath)]
			##current_path = current_path[:last_pos-1]

			temp = current_path.index(filepath)+len(filepath)
			current_path = current_path[:temp]
			print(f"sliced--------------------{current_path}")
			reloaded = True
			temp = current_path.index(filepath)
			current_path = current_path[:temp-1]
		print(f"updated--------------------{current_path}")
		#get path bfore current file i.e parent, so we fetch all files
		# repo/sub1/sub2, path should be repo to view sub1 
		main_tree =  fs_tree_to_dict(current_path)
		# print(f"main_tree={main_tree}")
		find_dirs(main_tree)
		print(f"alldirs={all_dirs}")
		if filepath in all_dirs: #display dir if dir
			if(reloaded):
				# session['current_path'] = current_path
				pass
			else:
				current_path = current_path+'/'+filepath
				session['current_path'] = current_path

			inside_dict =  fs_tree_to_dict(current_path)
			find_dirs(inside_dict)
			main_tree = fs_tree_to_dict(session['main_path'])
			return render_template('repo.html',trees=inside_dict,all_dirs=all_dirs,all_time=all_time,main_tree=main_tree)

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

@repo.route('/insert_file',methods=["POST","GET"])
def insert_file():
	if request.method == "POST":
		# path = os.path.abspath('static/student/')
		files = request.files.getlist('fileupload')
		for file in files:
			print(f'file={file}')
			filename = file.filename
			f = os.path.join(session['current_path'], file.filename)
			# f = os.path.join(, file.filename)
			file.save(f)
		return redirect(url_for('repository.index'))

@repo.route('/insert_folder',methods=["POST","GET"])
def insert_folder():
	if request.method == "POST":
		filename = request.form['foldername']
		folder = session['current_path'] + "/" + filename
		value = os.mkdir(folder)
		return redirect(url_for('repository.index'))

@repo.route('/delete_file/<filename>')
def delete_file(filename):
	print(f'request={request.method}')
	# if request.method == 'POST':

	delete_path = session['current_path']+"/"+filename
	path = os.path.abspath(delete_path)
	if not os.path.exists(path):
		print("no such file")
	else:
		os.remove(path)
		print("file removed")
	
	print(f'request.url={request.url}')
	print(f'request.script_root={request.script_root}')
	if "next" in request.url:
		return redirect(url_for('next',filepath=request.script_root))
	else:
		return redirect(url_for('repository.index'))

def filetype(file):
	file = file.lower()
	audio_types = ['mp3','flac','aac','wma','wav']
	video_types = ['avi','mp4','mkv','flv']
	file_types = ['pdf','xlxs','csv', 'docx']
	image_types = ['gif','png','jpeg','bmp','tiff']
	code_types = ['js','c','cpp','java','ts','py','json','html','css']
	if file in audio_types:
		return 'audio'
	elif file in video_types:
		return 'video'
	elif file in file_types:
		if file == 'pdf':
			return 'pdf'
		if file == 'xlxs':
			return 'xlxs'
		if file == 'docx':
			return 'docx'
		return 'unknown'
	elif file in image_types:
		return 'image'
	elif file in code_types:
		if file == 'js':
			return 'js'
		if file == 'html':
			return 'html'
		if file == 'css':
			return 'css'
		if file == 'py':
			return 'py'
		return 'file'
	else:
		return 'unknown'



@repo.route('/options/<file>')
def options(file):
	if request.method == "GET":
		info={}
		print(f"path = {session['current_path']}")
		file_dir = session['current_path']
		file_path = session['current_path']+'/'+file
		print(f"info = {os.stat(file_path)}")
		info['name'] = file
		all_time = gettime(file_dir)
		info['time'] = all_time[file]
		type_index = file.rindex(".")
		info['extension'] = file[type_index+1:]
		info['type'] = filetype(info['extension'])
		print(f"type===={info['type']}")

		return render_template("options.html",info=info)

@repo.route('/download/<filename>')
def download(filename):
	if request.method == "GET":
		return send_file(session['current_path']+'/'+filename, as_attachment=True ,cache_timeout=0)


@repo.route('/share/<file>/<filepath>')
def share(file,filepath):
	return file,filepath


@repo.route('/video')
def video():
	return render_template("video.html")

@repo.route('/videourl',methods=["GET","POST"])
def videourl():
	if request.method == 'POST':
		id = request.form['meeting']
	return redirect("meet.vallabh.tech/"+id)


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
