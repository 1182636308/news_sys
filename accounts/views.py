from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request

# 构建蓝图
from flask_login import login_user, logout_user, login_required

from forms import LoginForm, UserAddForm
from models import User, db

accounts = Blueprint('accounts', __name__, template_folder='templates', static_folder='static')


@accounts.route('/login', methods=['GET', 'POST'])
def login():
    # 用户登录
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        # 查找用户
        user = User.query.filter_by(username=username, password=password).first()
        if user is None:
            flash('用户名或者密码错误', 'warning')
        # 登录成功
        else:
            # 使用flask-login将user.id存到session中去
            login_user(user)
            flash('欢迎回来', 'success')

            return redirect(url_for('news.news_list'))
    return render_template('login.html', form=form)


@login_required
@accounts.route('/logout')
def logout():
    # 退出登录
    logout_user()
    flash('欢迎下次再来', 'success')
    return redirect('login')


@login_required
@accounts.route('/user/add', methods=['GET', 'POST'])
def user_add():
    # 新增用户
    form = UserAddForm()
    if form.validate_on_submit() and request.method == 'POST':
        password = form.data['password']
        password_repeat = form.data['password_repeat']
        if password != password_repeat:
            flash('两次输入的密码不一致', 'warning')
            return redirect(url_for('accounts.user_add'))
        # 将数据保存到数据库
        user_obj = User(
            username=form.data['username'],
            password=form.data['password'],
            email=form.data['email'],
            role=form.data['role'],
            created_at=datetime.now(),
            update_at=datetime.now()
        )
        db.session.add(user_obj)
        db.session.commit()
        # 消息提示
        flash('新增用户成功', 'success')
        # 跳转到用户列表
        return redirect(url_for('accounts.user_list'))
    else:
        # 消息提示
        if request.method == 'POST':
            flash('请修改错误后再提价，谢谢', 'warning')
            print(form.errors)

    return render_template('user_add.html', form=form)


@login_required
@accounts.route('/user/list/')
@accounts.route('/user/list/<int:page>')
def user_list(page=1):
    # 用户列表
    page_size = 5
    user_data = User.query.filter(User.is_valid == True).paginate(page=page, per_page=page_size)
    return render_template('user_list.html', user_data=user_data)


@login_required
@accounts.route('/user/delete<int:id>', methods=['GET', 'POST'])
def user_delete(id):
    #  删除用户
    user = User.query.get(id)
    if user is None:
        return 'no'
    user.is_valid = False
    db.session.commit()
    return 'ok'
