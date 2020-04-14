from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, ValidationError

from models import User
from utils import constants


class LoginForm(FlaskForm):
    # 用户登录表单
    username = StringField(label='用户名', render_kw={
        'class': 'form-control',
        'placeholder': '请输入用户名'
    }, validators=[DataRequired('用户名不能为空')])

    password = PasswordField(label='密码', render_kw={
        'class': 'form-control',
        'placeholder': '请输入密码'
    }, validators=[DataRequired('密码不能为空')])


class UserAddForm(FlaskForm):
    # 新增用户表单
    username = StringField(label='用户名', render_kw={
        'class': 'form-control',
        'placeholder': '请输入用户名'
    }, validators=[DataRequired('用户名不能为空')])

    password = PasswordField(label='密码', render_kw={
        'class': 'form-control',
        'placeholder': '请输入密码'
    }, validators=[DataRequired('密码不能为空')])

    password_repeat = PasswordField(label='重复密码', render_kw={
        'class': 'form-control',
        'placeholder': '请重复输入密码'
    }, validators=[DataRequired('密码不能为空')])

    email = StringField(label='邮箱', render_kw={
        'class': 'form-control',
        'placeholder': '请输入邮箱'
    }, validators=[DataRequired('邮箱不能为空')])

    role = SelectField(label='角色', choices=constants.ROLE_TYPE, render_kw={
        'class': 'form-control',
        'placeholder': '请输入角色'
    })

    def validate_username(self, field):
        # TODO用户名的验证
        username = field.data
        user = User.query.filter_by(username=username).first()
        print(user)
        if user:
            raise ValidationError('用户名已存在')
        return username


class NewsAddForm(FlaskForm):
    # 发表新闻表单
    title = StringField(label='新闻标题', render_kw={
        'class': 'form-control',
        'placeholder': '请输入新闻标题'
    }, validators=[DataRequired('新闻标题不能为空')])

    # 使用富文本编辑器
    content = CKEditorField(label='新闻正文', render_kw={
        'class': 'form-control',
    })
    is_top = SelectField(label='置顶级别', choices=constants.NEWS_TOPS, render_kw={
        'class': 'form-control',
    }, description='数字越大越靠前')
