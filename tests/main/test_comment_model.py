import unittest
from app import create_app, db
from app.models import Customer, Role, Comment, Article


class CommentModelTestCase(unittest.TestCase):

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
            role=Role.query.filter_by(role_name='Customer').first(),
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
        self.assertTrue(Customer.query.count() == 2)
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

    def test_attribute_and_function(self):
        """Comment的author属性、article属性"""
        self.assertTrue(self.comment.author.customer_id == self.jacob.customer_id)
        self.assertTrue(self.comment.article.article_id == self.article.article_id)
        self.assertTrue(self.jacob.comments.count() == 1)
        self.assertTrue(self.jacob.comments.first().comment_id == self.comment.comment_id)
        self.assertTrue(self.article.comments.count() == 1)
        self.assertTrue(self.article.comments.first().comment_id == self.comment.comment_id)

    def test_publish_comment(self):
        """发表评论"""
        # 游客禁止评论
        response = self.client.post('/publish_comment/{}'.format(self.article.article_id), json={'comment-content': '*em*'})
        self.assertTrue(response.status_code == 403)

        # Jacob评论
        self.login(self.jacob)
        response = self.client.post('/publish_comment/{}'.format(self.article.article_id), json={'comment-content': '*em*'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '评论成功，即将刷新页面')
        comment = self.article.comments.filter_by(comment_id=2).first()
        self.assertTrue(comment is not None)
        self.assertTrue(comment.author_id == self.jacob.customer_id)
        self.assertTrue(comment.content == '*em*')
