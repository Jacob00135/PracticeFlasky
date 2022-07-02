import unittest
from app import create_app, db
from app.models import Customer, Role, Comment, Article


class ManageCommentTestCase(unittest.TestCase):

    def setUp(self) -> None:
        # 创建应用
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        Role.insert_roles()

        # 插入测试数据
        self.xiejiyue = Customer(
            customer_id=1,
            customer_email='1466291943@qq.com',
            customer_name='XieJiyue',
            password='123456',
            role=Role.query.filter_by(role_name='Moderator').first(),
            confirmed=1,
            about_me='Python开发者'
        )
        self.jacob = Customer(
            customer_id=2,
            customer_email='2428207444@qq.com',
            customer_name='Jacob',
            password='123456',
            role=Role.query.filter_by(role_name='Customer').first(),
            confirmed=1,
            about_me='网站测试员'
        )
        self.admin = Customer(
            customer_id=3,
            customer_email='2026754775@qq.com',
            customer_name='FlaskyAdmin',
            password='123456',
            role=Role.query.filter_by(role_name='Administrator').first(),
            confirmed=1,
            about_me='Flasky管理员'
        )
        self.article = Article(
            article_id=1,
            title='标题',
            content='# 标题',
            author_id=self.xiejiyue.customer_id
        )
        self.comment = Comment(
            comment_id=1,
            content='*斜体*',
            author_id=self.jacob.customer_id,
            article_id=self.article.article_id
        )
        db.session.add_all([self.xiejiyue, self.jacob, self.article, self.comment])
        db.session.commit()

        # 检查插入数据是否成功
        self.assertTrue(Customer.query.count() == 3)
        self.assertTrue(Article.query.count() == 1)
        self.assertTrue(Comment.query.count() == 1)

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

    def test_manage_comment_page_403(self):
        """访问评论管理页面：游客、普通用户"""
        # 游客
        self.assertTrue(self.client.get('/manage_comment').status_code == 403)

        # 普通用户
        self.login(self.jacob)
        self.assertTrue(self.client.get('/manage_comment').status_code == 403)

    def test_manage_comment_page_moderator(self):
        """访问评论管理页面：协管员"""
        self.login(self.xiejiyue)
        self.assertTrue(self.client.get('/manage_comment').status_code == 200)

    def test_manage_comment_page_admin(self):
        """访问评论管理页面：管理员"""
        self.login(self.admin)
        self.assertTrue(self.client.get('/manage_comment').status_code == 200)

    def test_disable_comment_403(self):
        """禁用评论：无权限"""
        # 游客
        self.assertTrue(self.client.post('/update_comment_disabled', json={}).status_code == 403)

        # 普通用户
        self.login(self.jacob)
        self.assertTrue(self.client.post('/update_comment_disabled', json={}).status_code == 403)

    def test_disable_comment(self):
        """禁用评论、取消禁用评论"""
        # 登录协管员身份
        self.login(self.xiejiyue)

        # 禁用评论
        response = self.client.post('/update_comment_disabled', json={
            'comment_id': self.comment.comment_id,
            'disabled': 1
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '成功')
        self.assertTrue(self.comment.disabled)

        # 取消禁用评论
        response = self.client.post('/update_comment_disabled', json={
            'comment_id': self.comment.comment_id,
            'disabled': 0
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '成功')
        self.assertFalse(self.comment.disabled)
