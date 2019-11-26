from flask import Flask, jsonify, render_template, request, send_from_directory, redirect
from mong import Db
import os, datetime


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/home/gary/www/picture-db/imageg'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
db = Db()

def replace_images_id(mongo_ob_resp):
    # 多个文件
    images_list = []
    for image in mongo_ob_resp:
        id = image['_id']
        image.pop('_id')
        image['_id'] = str(id)
        images_list.append(image)
    return jsonify(images_list)
    
def get_file_ext(filename):
    ext = filename.rsplit('.')[-1]
    return ext

@app.route('/')
def index():
    images = replace_images_id(db.get_all_image())
    return images

@app.route('/tags')
def tags():
    tags = db.get_all_tags()
    return tags

@app.route('/tags/<string:tag>')
def find_by_tag(tag):
    images = db.get_images_by_tag(tag)
    images_list = replace_images_id(images)
    return images_list

@app.route('/upload', methods=("GET", "POST"))
def upload():
    msg = ''
    if request.method == 'POST':
        if 'file' not in request.files:
            msg = 'No file'
        
        file = request.files['file']
        if file.filename == '':
            msg = 'empty file'
            
        if file:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'test.jpg'))
        print(msg)
    return render_template('upload.html')

@app.route('/download/<string:id>')
def download(id):
    image = db.get_image_filename_by_id(id)
    # img_link = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    # print(app.config['UPLOAD_FOLDER'])
    # print(image_filename)
    # print(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
    filename = image['filename']
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/edit/<string:id>')
def edit(id):
    if request.method == 'POST':
        pass
    image = db.get_image_filename_by_id(id)
    # print(type(image))
    # image = replace_images_id(image)
    # print(image)
    return render_template('edit.html', image=image)

@app.route('/update/<string:_id>', methods=("GET", "POST"))
def update(_id):
    return _id