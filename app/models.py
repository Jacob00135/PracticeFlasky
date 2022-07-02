import os.path
from time import time as get_timestamp
from datetime import datetime
from pymysql import install_as_MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.jose import jwt
from flask_login import AnonymousUserMixin
from config import Config, ROLE_NAME_MAP, DEFAULT_HEAD_PORTRAIT, STATIC_HEAD_PORTRAIT_PATH
from . import db, login_manager
from .common_function import get_md5_encode

"""用户权限说明表：
英文名称         说明         权重
FOLLOW         关注用户        1
COMMENT   在他人文章中发表评论  2
WRITE          写文章          4
MODERATE  管理他人发表的评论    8
ADMIN         管理员权限       16"""
install_as_MySQLdb()


class Follow(db.Model):
    __tablename__ = 'follows'
    fans_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), primary_key=True)
    follow_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return "<Follow '{} - {}'>".format(self.fans.customer_name, self.author.customer_name)


class Comment(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    # content_html = db.Column(db.Text, nullable=False)
    comment_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.article_id'))

    # @staticmethod
    # def on_change_content(target, value, old_value, initiator):
    #     allow_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
    #     target.content_html = bleach.linkify(bleach.clean(
    #         markdown(value, output_format='html'),
    #         tags=allow_tags,
    #         strip=True
    #     ))

    def __repr__(self):
        return "<Comment '{}'>".format(self.comment_id)


class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    customer_name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'))
    confirmed = db.Column(db.Boolean, default=False)

    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    head_portrait = db.Column(db.String(64), default=DEFAULT_HEAD_PORTRAIT, nullable=False)

    articles = db.relationship('Article', backref='author', lazy='dynamic')

    follow_author = db.relationship(
        'Follow',
        foreign_keys=[Follow.fans_id],
        backref=db.backref('fans', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    fans = db.relationship(
        'Follow',
        foreign_keys=[Follow.author_id],
        backref=db.backref('author', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Customer, self).__init__(**kwargs)
        if self.role is None:
            administrator = Role.query.filter_by(role_name='Administrator').first()
            if self.customer_email == Config.FLASKY_ADMIN and administrator is not None:
                self.role = administrator
            else:
                self.role = Role.query.filter_by(is_default=True).first()

    @property
    def password(self):
        raise AttributeError('密码不是可读属性')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.customer_id)

    def generate_confirmation_token(self, data=None):
        if data is not None and not isinstance(data, dict):
            raise TypeError('输入的参数data只能是字典类型')
        if data is None:
            data = {}
        data.update({'now': get_timestamp(), 'customer_id': self.customer_id})
        token = jwt.encode({'alg': 'HS256'}, data, Config.SECRET_KEY)
        return token

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def get_head_portrait_full_path(self):
        return os.path.join(STATIC_HEAD_PORTRAIT_PATH, self.head_portrait)

    def update_customer_email(self, customer_email):
        self.customer_email = customer_email
        if self.head_portrait != DEFAULT_HEAD_PORTRAIT:
            old_path = os.path.join(Config.HEAD_PORTRAIT_PATH, self.head_portrait)
            new_head_portrait = get_md5_encode(self.customer_email) + '.' + self.head_portrait.split('.')[1]
            new_path = os.path.join(Config.HEAD_PORTRAIT_PATH, new_head_portrait)
            os.rename(old_path, new_path)
            self.head_portrait = new_head_portrait

    def update_head_portrait(self, filename):
        if self.head_portrait != DEFAULT_HEAD_PORTRAIT:
            os.remove(os.path.join(Config.HEAD_PORTRAIT_PATH, self.head_portrait))
        self.head_portrait = filename

    def follow(self, author):
        if author.customer_id is not None and not self.is_following(author) and self.customer_id != author.customer_id:
            f = Follow(fans=self, author=author)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, author):
        if author.customer_id is not None:
            f = self.follow_author.filter_by(author_id=author.customer_id).first()
            if f is not None:
                db.session.delete(f)
                db.session.commit()

    def is_following(self, cus):
        if cus.customer_id is None:
            return False
        return self.follow_author.filter_by(author_id=cus.customer_id).first() is not None

    def is_fans(self, cus):
        if cus.customer_id is None:
            return False
        return self.fans.filter_by(fans_id=cus.customer_id).first() is not None

    @property
    def follow_author_articles(self):
        """获取所关注的作者发布的文章，并按照发布时间排序，最新发布的在最前面"""
        # return db.session.query(Article).select_from(Follow).filter_by(fans_id=self.customer_id)\
        #     .join(Article, Follow.author_id == Article.author_id).order_by(Article.publish_time.desc())
        return Article.query.join(Follow, Follow.author_id == Article.author_id).\
            filter(Follow.fans_id == self.customer_id).order_by(Article.publish_time.desc())

    def __repr__(self):
        return "<Customer '{}'>".format(self.customer_name)


class Role(db.Model):
    __tablename__ = 'roles'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(255), unique=True, nullable=False)
    is_default = db.Column(db.Boolean, default=False, nullable=False, index=True)
    permissions = db.Column(db.Integer, default=0, nullable=False)
    customers = db.relationship('Customer', backref='role', lazy='dynamic')

    def get_chinese_role_name(self):
        return ROLE_NAME_MAP[self.role_name]

    def has_permission(self, perm):
        return (self.permissions & perm) == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions = self.permissions + perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions = self.permissions - perm

    def reset_permissions(self):
        self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'Customer': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'Customer'
        for role_name, perm_list in roles.items():
            role = Role.query.filter_by(role_name=role_name).first()
            if role is None:
                role = Role(role_name=role_name)
            role.permissions = sum(perm_list)
            if role_name == default_role:
                role.is_default = True
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role '{}'>".format(self.role_name)


class Permission(object):
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class AnonymousCustomer(AnonymousUserMixin):
    @staticmethod
    def can(perm):
        return False

    @staticmethod
    def is_administrator():
        return False


class Article(db.Model):
    __tablename__ = 'articles'
    article_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # content_html = db.Column(db.Text, nullable=False)
    publish_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))

    comments = db.relationship('Comment', backref='article', lazy='dynamic')

    # @staticmethod
    # def on_change_content(target, value, old_value, initiator):
    #     allow_tags = [
    #         'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
    #         'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'table', 'thead', 'tbody', 'tr', 'td', 'th', 'img', 'span'
    #     ]
    #     target.content_html = bleach.linkify(bleach.clean(
    #         markdown(value, output_format='html'),
    #         tags=allow_tags,
    #         strip=True
    #     ))

    # def get_publish_time_timestamp(self):
    #     return self.publish_time.replace(tzinfo=timezone.utc).timestamp() * 1000

    def __repr__(self):
        return "<Article '{}'>".format(self.title)


@login_manager.user_loader
def load_user(customer_id):
    return Customer.query.get(int(customer_id))


login_manager.anonymous_user = AnonymousCustomer
# db.event.listen(Article.content, 'set', Article.on_change_content)
# db.event.listen(Comment.content, 'set', Comment.on_change_content)
