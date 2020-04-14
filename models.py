import uuid

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class User(db.Model, UserMixin):
    # 用户表
    __tablename__ = 'accounts_user'
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    # 用户名
    username = db.Column(db.String(64), nullable=False)
    # 密码
    password = db.Column(db.String(255), nullable=False)
    # 邮箱
    email = db.Column(db.String(128), nullable=False)
    # 角色
    role = db.Column(db.String(20), nullable=False)
    # 逻辑删除按钮
    is_valid = db.Column(db.Boolean, default=True)
    # 管理员
    is_super = db.Column(db.Boolean, default=False)
    # 创建时间
    created_at = db.Column(db.DateTime)
    # 最后修改时间
    update_at = db.Column(db.DateTime)


class NewsType(db.Model):
    # 新闻类型表
    __tablename__ = 'news_type'
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    # 类型
    type = db.Column(db.String(64), nullable=False)
    # 创建时间
    created_at = db.Column(db.DateTime)
    # 最后修改时间
    update_at = db.Column(db.DateTime)


class News(db.Model):
    # 新闻表
    __tablename__ = 'news'
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    # UID
    uid = db.Column(db.String(128), nullable=False, default=uuid.uuid4, unique=True)
    # 标题
    title = db.Column(db.String(64), nullable=False)
    # 关联用户表，用户id
    user_id = db.Column(db.Integer, db.ForeignKey('accounts_user.id'))
    userobj = relationship(User, backref='userobj')
    # 关联新闻类型，并反向关系映射
    type_id = db.Column(db.Integer, db.ForeignKey('news_type.id'))
    typeobj = relationship(NewsType, backref='typeobj')
    # 新闻正文id,内容用MangoDB存储，
    content_id = db.Column(db.String(64), nullable=False)
    # 置顶级别
    is_top = db.Column(db.String(20))
    # 浏览次数
    view_count = db.Column(db.Integer, default=0)
    # 新闻状态
    status = db.Column(db.String(20), nullable=False)
    # 逻辑删除
    is_valid = db.Column(db.Boolean, default=True)
    # 审批人
    approvetor = db.Column(db.String(64))
    # 创建时间
    created_at = db.Column(db.DateTime)
    # 最后修改时间
    update_at = db.Column(db.DateTime)
