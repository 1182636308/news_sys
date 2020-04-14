import os

from flask import Flask, send_from_directory, render_template, request, url_for,redirect

from accounts.views import accounts
from models import db, User
from flask_ckeditor import CKEditor, upload_success, upload_fail
from flask_login import LoginManager, login_user, logout_user
from news.views import news
from utils import constants

app = Flask(__name__)

app.config.from_object('conf.Config')

# 使用ORM相关配置
db.init_app(app)
db.app = app
# 富文本编辑器的配置
ckeditor = CKEditor(app)

# 注册蓝图
app.register_blueprint(accounts, url_prefix='/accounts')
app.register_blueprint(news, url_prefix='/news')

# 用户登录相关的配置
login_manager = LoginManager()
login_manager.login_view = '/accounts/login'
login_manager.login_message = 'please login!'
login_manager.session_protection = 'strong'
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(err):
    # 重写404状态页面
    return render_template('base/not_found.html'), 404


@app.context_processor
def inject_const():
    # 添加上下文变量
    return dict({
        'constants': constants
    })


@app.route('/')
def hello_world():
    return redirect(url_for('news.news_list'))


# 富文本上传图片的相关配置
@app.route('/files/<path:filename>')
def uploaded_files(filename):
    path = './news/static/upload'
    return send_from_directory(path, filename)


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')  # 获取上传图片文件对象
    # Add more validations here
    extension = f.filename.split('.')[1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:  # 验证文件类型示例
        return upload_fail(message='Image only!')  # 返回upload_fail调用
    f.save(os.path.join('./news/static/upload', f.filename))
    url = url_for('uploaded_files', filename=f.filename)
    return upload_success(url=url)  # 返回upload_success调用


# login回调函数
@login_manager.user_loader
def user_loader(id):
    return db.session.query(User).filter_by(id=id).first()
