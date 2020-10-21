from flask import Blueprint, render_template, jsonify, url_for, redirect, request, session, flash, send_file
from flask_jwt_extended import (
	JWTManager, jwt_required, create_access_token,
	get_jwt_identity
)
import datetime, string
from database import mongo
from random import *
from functools import wraps
import os
from hurry.filesize import size
import zipfile

app = Blueprint('repository', __name__,template_folder='templates')



def random_chars(y):
    return ''.join(choice(string.ascii_letters) for x in range(y))


def zipfolder(foldername, target_dir):
    zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
    rootlen = len(target_dir) + 1
    for base, dirs, files in os.walk(target_dir):
        for file in files:
            fn = os.path.join(base, file)
            zipobj.write(fn, fn[rootlen:])



    
def get_extension(name):
    ext = "Folder"
    try:
        if (name.split('.')[1]):
            ext = name.split('.')[1].upper()
    except:
        pass
    if ext not in icons.keys():
        icon = 'icon-file-empty'
        ext = "Unknown"
    else:
        icon = icons[ext]
    return ext,icon


icons = {
    'PNG':'icon-image2',
    'JPEG':'icon-image2',
    'JPG':'icon-image2',
    'TIF':'icon-image2',
    'Folder':'icon-folder2',
    'MP3':'icon-music',
    'WAV':'icon-music',
    'MP4':'icon-file-video',
    'PDF':'icon-file-pdf',
    'TXT':'icon-file-text',
    'XLSX':'icon-file-stats',
    'PPTX':'icon-file-presentation',
    'CSS':'icon-file-css',
    'HTML':'icon-file-xml',
    'ZIP':'icon-file-zip',
    'RAR':'icon-file-zip',

}




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


# Check if user logged in
def is_authorised(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        current_dir = str(request.url)
        if session['username'] == current_dir.split('/')[2]:
            return f(*args, **kwargs)
        else:
            flash('You are not authodrized here', 'danger')
            return redirect(url_for('repository.index',current_dir = 'static/repository/'+session['username']))
        return wrap



@app.route('/<path:current_dir>', methods=['GET', 'POST'])
@is_logged_in
def index(current_dir):
    #validate for authorised access

    #if 'current_dir' in session:
    #    current_dir = session['current_dir']
    #else:
    #    current_dir = 'static/repository/'+session['username']
    #    session['current_dir'] = current_dir
    if session['username'] == current_dir.split('/')[2]:
        print(current_dir)
    else:
        flash('You are not authodrized here', 'danger')
        return redirect(url_for('repository.index',current_dir = 'static/repository/'+session['username']))

    path = os.path.abspath(current_dir)
    home_path = os.path.abspath('static/repository/'+session['username'])
    if not os.path.exists(home_path):
        os.makedirs(home_path)
    if not os.path.exists(path):
        flash("File or folder is not exist.","danger")
        return redirect(url_for('repository.index',current_dir = 'static/repository/'+session['username']))

    all_dirs = os.listdir(path)

    all_files = []

    for item in all_dirs:
        ext,icon = get_extension(item)
        all_files.append(
            {
                'name':item,
                'type': ext,
                'size': size(os.stat(path + '/' + item).st_size),
                'icon': icon
            }
        )

    back_link = '/'.join(current_dir.split('/')[:-1])

    return render_template("repository.html",current_dir = current_dir,all_files=all_files,back_link=back_link)



@app.route('/create_folder/<path:current_dir>/', methods=['POST'])
@is_logged_in
def create_folder(current_dir):
    if session['username'] == current_dir.split('/')[2]:
        pass
    else:
        flash('You are not authodrized here', 'danger')
        return redirect(url_for('repository.index',current_dir = 'static/repository/'+session['username']))
    #current_dir = session['current_dir']
    folder_name = request.form['folder_name']
    path = os.path.abspath(current_dir+'/'+folder_name)
    if not os.path.exists(path):
        os.makedirs(path)
        flash("Folder created succesfully","success")

    return redirect(url_for('repository.index',current_dir = current_dir))

@app.route('/upload_files/<path:current_dir>/', methods=['POST'])
@is_logged_in
def upload_files(current_dir):
    if session['username'] == current_dir.split('/')[2]:
        pass
    else:
        flash('You are not authodrized here', 'danger')
        return redirect(url_for('repository.index',current_dir = 'static/repository/'+session['username']))
    path = os.path.abspath(current_dir)

    if not os.path.exists(path):
        os.makedirs(path)
        flash("Folder created succesfully","success")

    if 'files' not in request.files:
            flash('No file part')
            return redirect(request.url)


    
    
    files = request.files.getlist('files')
    for file in files:
        print(file)
        f = os.path.join(path, file.filename)
        file.save(f)
    #file.seek(0, os.SEEK_END)
    #file_length = file.tell()
    #print(file_length)
    #if not file_length < 1024000 :
    #    flash('File size is greater than 1 mb','danger')
    #    return redirect(url_for('profile'))
    

    return redirect(url_for('repository.index',current_dir = current_dir))


@app.route('/delete_file/<path:current_dir>/', methods=['GET', 'POST'])
@is_logged_in
def delete_file(current_dir):
    #current_dir = session['current_dir']
    file_path = request.args.get('file_path')
    print(file_path)
    if session['username'] != file_path.split('/')[2]:
        flash("You are not authorised person to delete this file or folder.","danger")
        return redirect(url_for('repository.index',current_dir = current_dir))

    path = os.path.abspath(file_path)
    if os.path.exists(path):
        try:
            if path.split('/')[-1].split('.')[1]:
                os.remove(path)
                flash("File deleted succesfully","success")
        except:
            try:
                os.rmdir(path)
                flash("Folder deleted succesfully","success")
            except:
                flash("Can't delete file or folder","danger")
        
    else:
        flash("File doesn't exist","danger")
    return redirect(url_for('repository.index',current_dir = current_dir))








#use middleware to check authorised access
@app.route('/download/<path:file_name>/<file_type>/<path:current_dir>/', methods=['GET', 'POST'])
@is_logged_in
def download(file_name,file_type,current_dir):
    if session['username'] == current_dir.split('/')[2]:
        print(current_dir)
    else:
        flash('You are not authodrized here', 'danger')
        return redirect(url_for('repository.index',current_dir = 'static/repository/'+session['username']))
    path = os.path.abspath(current_dir + '/' + file_name)
    
    if os.path.exists(path):
        if file_type == "Folder":
            zip_file_name = file_name
            zip_save_path = os.path.abspath('static/repository/'+session['username']+'/'+zip_file_name)
            zipfolder(zip_save_path, path)
            result = send_file(zip_save_path + '.zip', as_attachment=True)
            os.remove(zip_save_path + '.zip')
        else:
            result = send_file(path, as_attachment=True)
        
        return result
    else:
        flash("No file or folder found","danger")
        return redirect(url_for('repository.index',current_dir = current_dir))    



@app.route('/sharing/<path:file_name>/<file_type>/<path:current_dir>/', methods=['GET', 'POST'])
def sharing(file_name,file_type,current_dir):
    repository = mongo.db.repositories
    if session['username'] == current_dir.split('/')[2]:
        pass
    else:
        flash('You are not authodrized here', 'danger')
        return redirect(url_for('repository.index',current_dir = 'static/repository/'+session['username']))
    path = os.path.abspath(current_dir + '/' + file_name)
    if os.path.exists(path):
        data = {
            'file_name':file_name,
            'file_type':file_type,
            'current_dir':current_dir + '/' + file_name
        }

        users = mongo.db.users
        all_users = users.find()

        users_data = {}
        branches = [
            'it',
            'computer',
            'mechanical'
        ]

        for b in branches:
            users_data[b] = users.find({'branch':b})


        repo = repository.find_one({'path':current_dir + '/' + file_name})

        if repo:
            shared_with = []
            for u in repo['shared_with']:
                shared_with.append(users.find_one({'username':u}))
            data['shared_with'] = shared_with
            
        
        if request.method == "POST":
            shared_users = request.form.getlist('shared_users')
            
            if repo:
                for username in shared_users:
                
                    repository.update_one({
                        'path':current_dir + '/' + file_name,
                        'owner':session['username']
                    },
                    {
                        '$addToSet':{ 'shared_with': username }
                    })

                    users.update_one({'username':username},{'$addToSet':{'shared_with_me':repo['repo_id']}})
                flash("Successfully shared","success")
                
            else:
                repo_id = random_chars(10) + str(randint(111,999))
                repository.insert_one({
                    'path':current_dir + '/' + file_name,
                    'owner':session['username'],
                    'shared_with':shared_users,
                    'type':file_type,
                    'repo_id':repo_id,
                    'size':size(os.stat(path).st_size)
                })
                for username in shared_users:
                    users.update_one({'username':username},{'$addToSet':{'shared_with_me':repo_id}})
                flash("Successfully shared","success")
            return redirect(url_for('repository.sharing',file_name=file_name,file_type=file_type,current_dir=current_dir))
        



    else:
        flash("No file exists","danger")
    return render_template("sharing.html",data = data,current_dir = current_dir,users_data = users_data)




@app.route('/unshare/<path:file_name>/<file_type>/<path:current_dir>/<username>')
def unshare(file_name,file_type,current_dir,username):
    path = current_dir + '/' + file_name
    try:
        repo = mongo.db.repositories.find_one_and_update({'path':path},{ '$pull': { 'shared_with': username } })
        mongo.db.users.update_one({'username':username},{'$pull':{'shared_with_me':repo['repo_id']}})
        flash("User unshared sueccessfully","success")
    except:
        flash("Something went wrong","danger")
    return redirect(url_for('repository.sharing',file_name=file_name,file_type=file_type,current_dir=current_dir))


@app.route('/shared_with_me/', methods=['GET', 'POST'])
def shared_with_me():
    user = mongo.db.users.find_one({'username':session['username']})
    repositories = mongo.db.repositories
    shared_repos = []
    if 'shared_with_me' in user:
        for repo_id in user['shared_with_me']:
            repo = repositories.find_one({'repo_id':repo_id})
            item = {
                'name' : repo['path'].split('/')[-1],
                'type' : repo['type'],
                'repo_id': repo['repo_id'],
                'path':repo['path'],
                'owner': repo['owner'],
                'size':repo['size']
            }
            shared_repos.append(item)


    return render_template("shared_with_me.html",shared_repos = shared_repos)





#use middleware to check authorised access
@app.route('/shared_download/<path:file_name>/<file_type>/<path:path>/', methods=['GET', 'POST'])
@is_logged_in
def shared_download(file_name,file_type,path):
    repo = mongo.db.repositories.find_one({'path':path})
    if session['username'] in repo['shared_with']:
        print("found")
    else:
        flash('You are not authodrized here', 'danger')
        return redirect(url_for('repository.shared_with_me'))

    path = os.path.abspath(path)
    
    if os.path.exists(path):
        if file_type == "Folder":
            zip_file_name = file_name
            zip_save_path = os.path.abspath('static/repository/'+session['username']+'/'+zip_file_name)
            zipfolder(zip_save_path, path)
            result = send_file(zip_save_path + '.zip', as_attachment=True)
            os.remove(zip_save_path + '.zip')
        else:
            result = send_file(path, as_attachment=True)
        
        return result
    else:
        flash("No file or folder found","danger")
        return redirect(url_for('repository.shared_with_me'))   




@app.route('/shared/<path:current_dir>', methods=['GET', 'POST'])
@is_logged_in
def shared(current_dir):
    #validate for authorised access

    #if 'current_dir' in session:
    #    current_dir = session['current_dir']
    #else:
    #    current_dir = 'static/repository/'+session['username']
    #    session['current_dir'] = current_dir
    if session['username'] == current_dir.split('/')[2]:
        print(current_dir)
    else:
        flash('You are not authodrized here', 'danger')
        return redirect(url_for('repository.index',current_dir = 'static/repository/'+session['username']))

    path = os.path.abspath(current_dir)
    home_path = os.path.abspath('static/repository/'+session['username'])
    if not os.path.exists(home_path):
        os.makedirs(home_path)
    if not os.path.exists(path):
        flash("File or folder is not exist.","danger")
        return redirect(url_for('repository.index',current_dir = 'static/repository/'+session['username']))

    all_dirs = os.listdir(path)

    all_files = []

    for item in all_dirs:
        ext,icon = get_extension(item)
        all_files.append(
            {
                'name':item,
                'type': ext,
                'size': size(os.stat(path + '/' + item).st_size),
                'icon': icon
            }
        )

    back_link = '/'.join(current_dir.split('/')[:-1])

    return render_template("repository.html",current_dir = current_dir,all_files=all_files,back_link=back_link)
