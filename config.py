import os.path
from os import urandom, environ
from logging import ERROR as LOG_LEVEL_ERROR
from logging.handlers import SMTPHandler

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_HEAD_PORTRAIT_PATH = '/static/customer/head_portrait'
DEFAULT_HEAD_PORTRAIT = 'default-head-portrait.png'
ROLE_NAME_MAP = {
    'Customer': '普通用户',
    'Moderator': '协管员',
    'Administrator': '管理员'
}
MYSQL_BASE_URI = 'mysql://{}:{}@{}/'.format(
    environ.get('MYSQL_USERNAME'),
    environ.get('MYSQL_PASSWORD'),
    environ.get('MYSQL_HOSTNAME')
)


class Config(object):
    # IP地址
    HOST = '127.0.0.1'
    PORT = '5000'

    # 会话秘钥
    SECRET_KEY = urandom(16)

    # 验证令牌的默认有效时长
    TOKEN_EFFECTIVE_TIME = 600

    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 电子邮件配置
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = environ.get('MAIL_USERNAME')

    # 指定管理员的邮箱
    FLASKY_ADMIN = environ.get('FLASKY_ADMIN')

    # 上传文件相关
    MAX_CONTENT_LENGTH = 1024 * 1024  # 限制上传文件的大小为1MB
    HEAD_PORTRAIT_PATH = os.path.join(BASE_DIR, 'app/static/customer/head_portrait')

    # 文章列表的一页可显示的最大文章数量
    FLASKY_MAX_ARTICLE_NUMBER = 20

    # 用户列表的一页可显示的最大用户数量
    FLASKY_MAX_CUSTOMER_NUMBER = 20

    # 文章评论的一页可显示的最大评论数量
    FLASKY_MAX_COMMENT_NUMBER = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = MYSQL_BASE_URI + 'flasky'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = MYSQL_BASE_URI + 'flasky_test'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = MYSQL_BASE_URI + 'flasky'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # 出错时邮件通知管理员
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + 'Flasky错误日志',
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(LOG_LEVEL_ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
