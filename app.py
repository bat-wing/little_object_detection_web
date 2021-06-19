import base64
import io
import os

from flask import Flask, jsonify, request, render_template, make_response, send_from_directory, redirect, flash
from flask_login import LoginManager, login_required, login_user, logout_user
from PIL import Image
from werkzeug.utils import secure_filename
from datetime import timedelta

from funcUtil import Pic_str
from user_model import User

from inference_service import InferenceService


app = Flask(__name__)
inferenceService = InferenceService()

# 图片部分初始化
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
SAVE_FOLDER = 'static/save'
app.config['SAVE_FOLDER'] = SAVE_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'JPG', 'PNG', 'jpeg', 'JPEG'}


# login初始化
app.secret_key = 'skajfkl'
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.login_message = u"用户未登录，请先登录。"
login_manager.init_app(app)


# 用户列表
# user_list = list()


@login_manager.user_loader
def load_user(user_id):
    user = User()
    return user


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 登陆界面
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


# 登录判断
@app.route('/')
@app.route('/login_judge', methods=['GET', 'POST'])
def login_judge():
    if request.form['password'] == '123' and request.form['id'] == 'qwe':
        user = User()
        login_user(user)
        return redirect('/upload')
    else:
        flash('用户名或密码错误！')
        return render_template('login.html')


# 显示使用记录页面
@app.route('/history', methods=['POST', 'GET'])
@login_required
def history():
    with open(r".\static\user\qwe_history.txt", "r") as f:  # 打开文件
        data = f.read()  # 读取文件
        f.close()
        list_data = data.split('\n')
        length = len(list_data) - 1
        if length == 0:
            return render_template('history.html', len=0, name=None, sum=None, g_num=None, b_num=None)
        # 制作四个列表，分别为照片名、葡萄总数、好葡萄数、坏葡萄数
        name, sum, g_num, b_num = [], [], [], []
        for i in range(length):
            x = list_data[i].split(' ')
            name.append(x[0])
            sum.append(x[1])
            g_num.append(x[2])
            b_num.append(x[3])
    return render_template('history.html', len=length, name=name, sum=sum, g_num=g_num, b_num=b_num)


# 显示次数
@app.route('/times', methods=['POST', 'GET'])
def times():
    with open(r".\static\manager\user_times.txt", "r") as f:  # 打开文件
        data = f.read()  # 读文件
        f.close()
        list_data = data.split('\n')
        length = len(list_data) - 1
        if length == 0:
            return render_template('times.html', len=0, name=None, used=None, surplus=None)
        name, used, surplus = [], [], []
        for i in range(length):
            x = list_data[i].split(' ')
            name.append(x[0])
            used.append(x[1])
            surplus.append(x[2])
    return render_template('times.html', len=length, name=name, used=used, surplus=surplus)

# @app.route('/logout', methods=['GET', 'POST'])
# @login_required
# def logout():
#     logout_user()
#     return "logout page"
#
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     return render_template('register.html')
#
#
# @app.route('/creat_user', methods=['GET', 'POST'])
# def creat_user():
#     a = list()
#     for i in user_list:
#         if request.form['id'] == i.id:
#             flash('用户名已存在！')
#             return redirect('/register')
#     a.append(request.form['id'])
#     a.append(request.form['password'])
#     if request.form['password'] != request.form['password-']:
#         flash('两次输入密码不相同')
#         return redirect('/register')
#     a.append(request.form['email'])
#     a.append(int(request.form['phone']))
#     user_list.append(User(a))
#     print(user_list)
#     return redirect('/login')


# 调用api
@app.route('/api/<string:filename>', methods=['POST', 'GET'])
def main(filename):
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    image = Image.open(os.path.join(file_dir, '%s' % filename))
    g, b, image = inferenceService.inference(image)
    # 储存输出照片
    file_dir_save = os.path.join(basedir, app.config['SAVE_FOLDER'])
    if not os.path.exists(file_dir_save):
        os.makedirs(file_dir_save)
    file_add = os.path.join(file_dir_save, filename)
    image.save(file_add, quality=95)
    with open(r".\static\user\qwe_history.txt", "a") as f:
        f.write(filename + ' ' + str(g+b) + ' ' + str(g) + ' ' + str(b) + '\n')
        f.close()

    with open(r".\static\manager\user_times.txt", "r") as f:
        data = f.read()  # 读文件
        list_data = data.split('\n')
        length = len(list_data) - 2
        data = list_data[length].split(' ')
        data[1] = str(int(data[1])+1)
        data[2] = str(int(data[2])-1)
        list_data.pop()
        list_data.pop()
    f = open(r".\static\manager\user_times.txt", "w")
    for i in list_data:
        f.write(i + '\n')
    f.write(data[0] + ' ' + data[1] + ' ' + data[2] + '\n')
    f.close()

    return render_template('upload_ok.html', fname=filename, quantity=g+b, g=g, b=b)


# 上传图片页面
@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload_test():
    with open(r".\static\manager\user_times.txt", "r") as f:  # 打开文件
        data = f.read()  # 读文件
        f.close()
        list_data = data.split('\n')
        length = len(list_data) - 2
        data = list_data[length].split(' ')
        print(data)
        data[2] = int(data[2])
    return render_template('up.html', data=data)


# 上传文件
@app.route('/up_photo', methods=['POST'], strict_slashes=False)
@login_required
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['photo']
    if f and allowed_file(f.filename):
        fname = secure_filename(f.filename)
        print(fname)
        ext = fname.rsplit('.', 1)[1]
        new_filename = Pic_str().create_uuid() + '.' + ext
        f.save(os.path.join(file_dir, new_filename))
        return redirect('/api/{}'.format(new_filename))
    else:
        flash('上传失败!只允许上传png, jpg, jpeg格式的图片。')
        return render_template('up.html')


# # 下载图片（无链接调用）
# @app.route('/download/<string:filename>', methods=['GET'])
# @login_required
# def download(filename):
#     if request.method == "GET":
#         file_dir_save = os.path.join(basedir, app.config['SAVE_FOLDER'])
#         file_add = os.path.join(file_dir_save, filename)
#         if os.path.isfile(file_add):
#             return send_from_directory(file_dir_save, filename, as_attachment=True)
#         pass
#
#
# # 单独展示图片（无链接调用）
# @app.route('/show/<string:filename>', methods=['GET'])
# @login_required
# def show_photo(filename):
#     file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
#     if request.method == 'GET':
#         if filename is None:
#             pass
#         else:
#             image_data = open(os.path.join(file_dir, '%s' % filename), "rb").read()
#             response = make_response(image_data)
#             response.headers['Content-Type'] = 'image/png'
#             return response
#     else:
#         pass


# wx支付
@app.route('/weixin', methods=['POST', 'GET'])
def weixin():
    return render_template("weixin.html")


# zfb支付
@app.route('/zfb', methods=['POST', 'GET'])
def zfb():
    return render_template("zfb.html")


if __name__ == '__main__':
    app.run(debug=True)
