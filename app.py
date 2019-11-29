from flask import Flask, jsonify, render_template, request, send_from_directory, redirect, url_for, flash
from mong import Db
import os, time, datetime


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/imageg'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = b'_5#y2L"KO89.\n\xec]/'

db = Db()

# 解决mongodb object（ObjectId）不能序列化问题，目前只能用于返回mongo_cursor多个字段
def replace_images_id(mongo_ob_resp):
    # 多个文件
    images_list = []
    for image in mongo_ob_resp:
        id = image['_id']
        image.pop('_id')
        image['_id'] = str(id)
        images_list.append(image)
    return images_list

# 获取文件扩展名
def get_file_ext(filename):
    ext = filename.rsplit('.')[-1].lower()
    return ext

# 首页用来显示所有的图片以及图片所属信息
@app.route('/')
def index():
    images = replace_images_id(db.get_all_image())
    # print(type(images))
    return render_template('images.html', images=images)

# 显示所有的标签以及相关图片数量
@app.route('/tags')
def tags():
    tags = db.get_all_tags()
    return render_template('tags.html', tags=tags)

#标签搜索
@app.route('/tag/')
def search_by_tag():
    tag = request.args['tag']
    return redirect(url_for('find_by_tag', tag=tag))


# 显示带有此标签的所有图片
@app.route('/tags/<string:tag>')
def find_by_tag(tag):
    images = db.get_images_by_tag(tag)
    # print(images)
    images_list = replace_images_id(images)
    # print(images_list)
    return render_template('images.html', images=images_list)

# 删除图片
@app.route('/delete/<string:id>')
def delete_image(id):
    image_file = os.path.join(app.config['UPLOAD_FOLDER'], db.delete_image_by_id(id))
    # print(image_file)
    os.remove(image_file)
    return redirect(url_for('index'))

# 上传图片文件
#　TODO　上传多个图片，上传时修改标签还是之后统一修改
@app.route('/upload', methods=("GET", "POST"))
def upload():
    
    if request.method == 'POST':
        error = ''
        if 'file' not in request.files:
            error = 'No file'
            
        file = request.files['file']
        if file.filename == '':
            error = 'empty file'
        if error == '':
            # 文件无问题
            filename = str(int(time.time())) + '.' + get_file_ext(file.filename)
            # 保存文件
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # 插入数据库
            image_info = {
                'filename':filename,
                'created_time':datetime.datetime.utcnow(),
                'uploader':'gary',
                'rate':5,
                'group':[],
                'tags':[]

            }
            # print(image_info)
            # 获取图片id
            id = db.add_new_image(image_info)
            # print(str(id.inserted_id))
            # 跳转图片编辑页面
            return redirect(url_for('edit',id=id.inserted_id))
        else:
            flash(error)
    return render_template('upload.html')

# 根据id下载图片
# TODO 批量下载
@app.route('/download/<string:id>')
def download(id):
    image = db.get_image_by_id(id)
    # img_link = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
    # print(app.config['UPLOAD_FOLDER'])
    # print(image_filename)
    # print(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
    filename = image['filename']
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

#更新单张图片信息
@app.route('/edit/<string:id>', methods=("GET", "POST"))
def edit(id):
    image = db.get_image_by_id(id)
    if image == None:
        flash('No image!')

    if request.method == 'POST':
    # 通过前端中的表单信息更新图片标签
    # 刷新重复提交问题，通过检查tag标签的唯一性，使重复提交无意义
    # TODO 前端设置js控件，控制表格提交按钮，防止重复提交
        
        #id 好像有点多多余，可以直接利用url中的id
        # id = request.form['id'] 
        
        newTag = request.form['addtag']
        # print(newTag)
        db.insert_image_tag(id,newTag)

        # 通过重定向改“POST” 为 “GET” 解决刷新重复提交
        return redirect(url_for('edit', id=id))

    
    return render_template('edit.html', image=image)

# 暂时无用,用来更新图片有带
@app.route('/update/<string:_id>', methods=("GET", "POST"))
def update(_id):
    return _id


