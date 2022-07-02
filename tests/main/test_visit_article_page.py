import unittest
from datetime import datetime
from app import create_app, db
from app.models import Article, Customer, Role


class VisitArticlePageTestCase(unittest.TestCase):

    def setUp(self) -> None:
        # 创建应用
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        Role.insert_roles()

        # 插入测试数据
        self.cus = Customer(
            customer_id=1,
            customer_email='2428207444@qq.com',
            customer_name='Jacob',
            password='123456',
            role=Role.query.filter_by(role_name='Customer').first(),
            confirmed=1,
            about_me='一名Python工程师'
        )
        self.moderator = Customer(
            customer_id=2,
            customer_email='1466291943@qq.com',
            customer_name='XieJiyue',
            password='123456',
            role=Role.query.filter_by(role_name='Moderator').first(),
            confirmed=1,
            about_me='软件测试员'
        )
        self.admin = Customer(
            customer_id=3,
            customer_email='flasksender@qq.com',
            customer_name='FlaskyAdmin',
            password='123456',
            role=Role.query.filter_by(role_name='Administrator').first(),
            confirmed=1,
            about_me='Flasky管理员'
        )
        self.cus_article_1 = Article(
            article_id=1,
            title='标题1',
            content='# 标题1',
            publish_time=datetime.utcnow(),
            author=self.cus
        )
        self.cus_article_2 = Article(
            article_id=2,
            title='标题2',
            content='# 标题2',
            publish_time=datetime.utcnow(),
            author=self.cus
        )
        self.moderator_article_1 = Article(
            article_id=3,
            title='标题3',
            content='# 标题3',
            publish_time=datetime.utcnow(),
            author=self.moderator
        )
        self.moderator_article_2 = Article(
            article_id=4,
            title='标题4',
            content='# 标题4',
            publish_time=datetime.utcnow(),
            author=self.moderator
        )
        db.session.add_all([
            self.cus,
            self.moderator,
            self.admin,
            self.cus_article_1,
            self.cus_article_2,
            self.moderator_article_1,
            self.moderator_article_2
        ])
        db.session.commit()
        self.assertTrue(len(Customer.query.all()) == 3)
        self.assertTrue(len(Article.query.all()) == 4)

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, cus):
        response = self.client.post('/auth/login', json={
            'email': cus.customer_email,
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '登录成功')
        self.assertTrue(response.json['next'] == '/')

    def test_visit_article_page(self):
        """访问文章页面"""
        for i in range(1, 5):
            response = self.client.get('/article/{}'.format(i))
            self.assertTrue(response.status_code == 200)

    def test_anonymous_visit_edit_article_page(self):
        """访问编辑文章页面：匿名用户"""
        response = self.client.get('/edit_article/1')
        self.assertTrue(response.status_code == 403)

    def test_customer_visit_edit_article_page(self):
        """访问编辑文章页面：普通用户"""
        self.login(self.cus)
        response = self.client.get('/edit_article/1')
        self.assertTrue(response.status_code == 200)
        response = self.client.get('/edit_article/3')
        self.assertTrue(response.status_code == 403)

    def test_administrator_visit_edit_article_page(self):
        """访问编辑文章页面：管理员"""
        self.login(self.admin)
        response = self.client.get('/edit_article/1')
        self.assertTrue(response.status_code == 200)
        response = self.client.get('/edit_article/3')
        self.assertTrue(response.status_code == 200)

    def test_anonymous_edit_article(self):
        """编辑文章：匿名用户"""
        response = self.client.post('/edit_article/1', json={'article-content': '标题1.1'})
        self.assertTrue(response.status_code == 403)

    def test_customer_edit_article(self):
        """编辑文章：普通用户"""
        self.login(self.cus)
        response = self.client.post('/edit_article/1', json={'article-content': '## 标题1'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '修改成功')
        self.assertTrue(self.cus_article_1.content == '## 标题1')
        response = self.client.post('/edit_article/3', json={'article-content': '## 标题3'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '无权操作')

    def test_administrator_edit_article(self):
        """编辑文章：管理员"""
        self.login(self.admin)
        response = self.client.post('/edit_article/1', json={'article-content': '## 标题1'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '修改成功')
        self.assertTrue(self.cus_article_1.content == '## 标题1')
        response = self.client.post('/edit_article/3', json={'article-content': '## 标题3'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '修改成功')
        self.assertTrue(self.moderator_article_1.content == '## 标题3')
