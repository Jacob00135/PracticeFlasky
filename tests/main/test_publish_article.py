import unittest
from pyquery import PyQuery
from app import create_app, db
from app.models import Article, Customer, Role


class PublishArticleTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        Role.insert_roles()
        self.cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='Jacob',
            password='123456',
            role=Role.query.filter_by(role_name='Customer').first(),
            confirmed=1,
            about_me='一名Python工程师'
        )
        self.moderator = Customer(
            customer_email='1466291943@qq.com',
            customer_name='XieJiyue',
            password='123456',
            role=Role.query.filter_by(role_name='Moderator').first(),
            confirmed=1,
            about_me='软件测试员'
        )
        self.admin = Customer(
            customer_email='flasksender@qq.com',
            customer_name='FlaskyAdmin',
            password='123456',
            role=Role.query.filter_by(role_name='Administrator').first(),
            confirmed=1,
            about_me='Flasky管理员'
        )
        db.session.add_all([self.cus, self.moderator, self.admin])
        db.session.commit()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, cus):
        response = self.client.post('/auth/login', json={'email': cus.customer_email, 'password': '123456'})
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

    def test_anonymous_show_article(self):
        """展示文章：对游客"""
        response = self.client.get('/')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(PyQuery(response.text)('#publish-article-form')) == 0)

    def test_customer_show_article(self):
        """展示文章：对用户"""
        self.login(self.cus)
        response = self.client.get('/')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(PyQuery(response.text)('#publish-article-form')) == 1)

    def test_anonymous_publish_article(self):
        """发布文章：游客身份"""
        response = self.client.post('/publish_article', json={'content': '空空如也'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '没有权限')

    def test_customer_publish_article(self):
        """发布文章：用户身份"""
        self.login(self.moderator)
        response = self.client.post('/publish_article', json={'article-title': '大标题', 'article-content': '空空如也'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '发布成功，即将刷新页面')
        article_list = Article.query.all()
        self.assertTrue(len(article_list) == 1)
        self.assertTrue(article_list[0].title == '大标题')
        self.assertTrue(article_list[0].content == '空空如也')
        self.assertTrue(article_list[0].author_id == self.moderator.customer_id)
