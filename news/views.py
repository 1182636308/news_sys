import uuid
from datetime import datetime

from flask import Blueprint, render_template, request, flash, redirect, url_for

# 构建蓝图
from flask_login import current_user, login_required
from sqlalchemy import text

from db.mongo_news import MongoNewsDao
from db.redis_dao import RedisNewsDao
from forms import NewsAddForm
from models import NewsType, db, News

news = Blueprint('news', __name__, template_folder='templates', static_folder='static')

# mongo数据库对象
mongo_bd = MongoNewsDao()
# redis数据库对象
redis_db = RedisNewsDao()


@login_required
@news.route('/list')
@news.route('/list/<int:page>')
def news_list(page=1):
    # 新闻列表
    news_obj = News.query.filter(News.user_id == current_user.id, News.is_valid == True)
    # 按id从大到小排序,并分页
    page_size = 5
    name = request.args.get('name', None)
    if name:
        news_obj = News.query.filter(News.user_id == current_user.id, News.is_valid == True,
                                     News.title.contains(name))
        news_data = news_obj.order_by(text('-id')).paginate(page=page, per_page=page_size)
    else:
        news_data = news_obj.order_by(text('-id')).paginate(page=page, per_page=page_size)
    return render_template('news_list.html', news_data=news_data)


@login_required
@news.route('/add', methods=['GET', 'POST'])
def news_add():
    # 发表新闻
    form = NewsAddForm()
    news_type_list = NewsType.query.all()
    if form.validate_on_submit() and request.method == 'POST':
        # 获取用户id,和新闻类型id
        user_id = current_user.id
        type_id = request.values['news_type']
        # 将数据保存到数据库
        # 将新闻正文保存到mongo数据库，将其id存到mysql数据库
        uid = uuid.uuid4()
        mongo_bd.insert_news(uid=uid, title=form.data['title'], content=form.data['content'])
        content_id = mongo_bd.search_id(uid=uid)
        news_obj = News(
            uid=uid,
            user_id=user_id,
            type_id=type_id,
            title=form.data['title'],
            content_id=content_id,
            is_top=form.data['is_top'],
            status='待审批',
            is_valid=True,
            created_at=datetime.now(),
            update_at=datetime.now()
        )
        db.session.add(news_obj)
        db.session.commit()
        # 消息提示
        flash('发表新闻成功', 'success')
        # 跳转到用户列表
        return redirect(url_for('news.news_list'))
    else:
        # 消息提示
        if request.method == 'POST':
            flash('请修改错误后再提价，谢谢', 'warning')
            print(form.errors)
    return render_template('news_add.html', form=form, news_type_list=news_type_list)


@login_required
@news.route('/edit/<uid>', methods=['GET', 'POST'])
def news_edit(uid):
    # 编辑新闻
    news_obj = News.query.filter_by(uid=uid, is_valid=True).first_or_404()
    news_type_list = NewsType.query.all()
    form = NewsAddForm(obj=news_obj)
    # 从mongodb取数据，然后赋值给form表单渲染到页面
    content = mongo_bd.search_content(news_obj.content_id)
    form.content.data = content
    search_name = request.args.get('name', '')
    if form.validate_on_submit():
        news_obj.title = form.data['title']
        news_obj.is_top = form.data['is_top']
        news_obj.type_id = request.values['news_type']
        db.session.commit()
        # 同步修改mongodb数据数据库
        mongo_bd.update(news_obj.content_id, form.data['title'], request.values['content'])
        flash('修改成功', 'success')
        search_name = request.values.get('search_name', '')
        return redirect('{0}?name={1}'.format(url_for('news.news_list'), search_name))
    else:
        print(form.errors)

    return render_template('news_edit.html', form=form, news_obj=news_obj,
                           search_name=search_name, news_type_list=news_type_list)


@login_required
@news.route('/delete/<uid>', methods=['GET', 'POST'])
def news_delete(uid):
    # 删除新闻
    news_obj = News.query.filter_by(uid=uid, is_valid=True).first_or_404()
    if news_obj is None:
        return 'on'
    # 如果新闻是已审批的，那么也要同步删除redis
    if news_obj.status == '已审批':
        redis_db.delete_cache(news_obj.id)
    # 先删除mongodb对应的数据
    mongo_bd.delete(news_obj.content_id)
    # 再删除mysql的
    news_obj.is_valid = False
    db.session.commit()
    return 'ok'


@login_required
@news.route('/review/list')
@news.route('/review/list/<int:page>')
def news_review_list(page=1):
    # 要审批新闻的列表
    # 获取所有未审批的新闻列表
    news_obj = News.query.filter_by(is_valid=True, status='待审批')
    page_size = 5
    news_data = news_obj.order_by(text('-id')).paginate(page=page, per_page=page_size)
    return render_template('news_review_list.html', news_data=news_data)


@login_required
@news.route('/review/<uid>', methods=['GET', 'POST'])
def news_review(uid):
    # 审批新闻
    news_obj = News.query.filter_by(uid=uid, is_valid=True).first_or_404()
    if news_obj is None:
        return 'on'
    # 新闻编辑的名字,类型，正文内容
    username = news_obj.userobj.username
    type = news_obj.typeobj.type
    content = mongo_bd.search_content(news_obj.content_id)
    # 把已审批的新闻存到Redis中
    redis_db.insert_news(news_obj.id, news_obj.uid, news_obj.title,
                         username, type, content, news_obj.is_top, str(news_obj.created_at))
    # 获取审批人的用户名
    approvetor = current_user.username
    news_obj.status = '已审批'
    news_obj.approvetor = approvetor
    db.session.commit()
    return 'ok'


@login_required
@news.route('/detail/<uid>', methods=['GET', 'POST'])
def news_detail(uid):
    # 新闻详情
    news_obj = News.query.filter_by(uid=uid, is_valid=True).first_or_404()
    news_type_list = NewsType.query.all()
    form = NewsAddForm(obj=news_obj)
    # 从mongodb取数据，然后赋值给form表单渲染到页面
    content = mongo_bd.search_content(news_obj.content_id)
    form.content.data = content
    return render_template('news_detail.html', form=form, news_type_list=news_type_list, news_obj=news_obj)


@login_required
@news.route('/reviewed/list')
@news.route('/reviewed/list/<int:page>')
def news_reviewed_list(page=1):
    # 已审批新闻列表
    news_obj = News.query.filter_by(is_valid=True, status='已审批')
    page_size = 5
    news_data = news_obj.order_by(text('-id')).paginate(page=page, per_page=page_size)
    return render_template('news_reviewed_list.html', news_data=news_data)


@login_required
@news.route('/review/back/<uid>', methods=['GET', 'POST'])
def review_back(uid):
    # 退回已审批的新闻
    news_obj = News.query.filter_by(uid=uid, is_valid=True, status='已审批').first_or_404()
    if news_obj is None:
        return 'on'
    redis_db.delete_cache(news_obj.id)
    news_obj.status = '待审批'
    db.session.commit()
    return 'ok'
