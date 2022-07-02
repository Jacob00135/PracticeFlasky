import unittest
from time import time as get_timestamp
from pyquery import PyQuery
from authlib.jose import jwt
from app import create_app, db
from app.models import Customer
from config import Config


class RegisterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_name='testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_email_exists(self):
        """ 注册检查：邮箱已被注册"""
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456',
            confirmed=1
        )
        db.session.add(cus)
        db.session.commit()
        response = self.client.post('/auth/register', json={
            'email': '2428207444@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '邮箱已被注册')

    def test_name_exists(self):
        """ 注册检查：用户名已存在"""
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456',
            confirmed=1
        )
        db.session.add(cus)
        db.session.commit()
        response = self.client.post('/auth/register', json={
            'email': '2026754775@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '用户名已存在')

    def test_send_success(self):
        """注册检查：成功发送确认邮件"""
        response = self.client.post('/auth/register', json={
            'email': '2428207444@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '确认邮件已发送至邮箱，请前往确认')

    def test_same_unconfirmed_register(self):
        """注册检查：
        1.发送注册请求，不确认
        2.发送与上一次相同邮箱、相同用户名的邮箱请求，不确认"""

        # 第一次
        response = self.client.post('/auth/register', json={
            'email': '2428207444@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '确认邮件已发送至邮箱，请前往确认')
        old_id = Customer.query.filter_by(customer_email='2428207444@qq.com').first().customer_id

        # 第二次
        response = self.client.post('/auth/register', json={
            'email': '2428207444@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '确认邮件已发送至邮箱，请前往确认')
        new_id = Customer.query.filter_by(customer_email='2428207444@qq.com').first().customer_id

        # 检查数据库中的新旧id是否一致
        self.assertTrue(old_id != new_id)

    def test_unlike_unconfirmed_register(self):
        """注册检查：
        1.发送注册请求，不确认
        2.发送与上一次相同邮箱、不相同用户名的邮箱请求，不确认
        3.数据库中已存在相同的用户名"""
        # 插入一个之后会导致用户名重复的数据
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue2',
            password='123456',
            confirmed=1
        )
        db.session.add(cus)
        db.session.commit()

        # 第一次
        response = self.client.post('/auth/register', json={
            'email': '2026754775@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '确认邮件已发送至邮箱，请前往确认')

        # 第二次
        response = self.client.post('/auth/register', json={
            'email': '2026754775@qq.com',
            'customer-name': 'XieJiyue2',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '用户名已存在')

    def test_unlike_unconfirmed_register_2(self):
        """注册检查：
        1.发送注册请求，不确认
        2.发送与上一次相同邮箱、不相同用户名的邮箱请求，不确认
        3.数据库中没有存在相同的用户名"""
        # 第一次
        response = self.client.post('/auth/register', json={
            'email': '2026754775@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '确认邮件已发送至邮箱，请前往确认')

        # 第二次
        response = self.client.post('/auth/register', json={
            'email': '2026754775@qq.com',
            'customer-name': 'XieJiyue2',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '确认邮件已发送至邮箱，请前往确认')

    def test_resend_email_invalid(self):
        """注册检查：
        1.成功发送邮件
        2.重新发送邮件，但是邮箱已被更改"""
        # 第一次
        response = self.client.post('/auth/register', json={
            'email': '2428207444@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '确认邮件已发送至邮箱，请前往确认')

        # 第二次
        response = self.client.post('/auth/send_confirm/register', json={
            'email': '2026754775@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '邮件发送失败，请检查邮箱是否填写正确')

    def test_resend_email_invalid_2(self):
        """注册检查：
        1.成功发送邮件
        2.重新发送邮件，但是邮箱已被确认过"""
        # 插入一个已注册成功的用户
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456',
            confirmed=1
        )
        db.session.add(cus)
        db.session.commit()

        # 第二次
        response = self.client.post('/auth/send_confirm/register', json={
            'email': '2428207444@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '该邮件已确认注册，请前往登录页面')

    def test_resend_email_success(self):
        """注册检查：
        1.成功发送邮件
        2.重新发送邮件，并且成功"""
        response = self.client.post('/auth/register', json={
            'email': '2428207444@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '确认邮件已发送至邮箱，请前往确认')

        # 第二次
        response = self.client.post('/auth/send_confirm/register', json={
            'email': '2428207444@qq.com',
            'customer-name': 'XieJiyue',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '再次发送邮件成功，请前往邮箱确认')

    def test_no_token(self):
        """令牌检验：没有令牌"""
        response = self.client.get('/auth/register_confirm')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(PyQuery(response.text)('h2.info').text() == '')

    def test_fake_token(self):
        """令牌检验：伪造令牌"""
        response = self.client.get('/auth/register_confirm?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub3ciOjE2NTEyMTc4ODEuNjUxNTY1OCwiY3VzdG9tZXJfaWQiOjE5fQ._yHihk9hyzzsDZmVHhGCvhqGInn1PpWqnPA7lHxAVb8')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(PyQuery(response.text)('.jumbotron .h3').text() == '验证失败，无效链接')

    def test_timeout_token(self):
        """令牌检验：超时令牌"""
        # 生成令牌
        token = jwt.encode(
            {'alg': 'HS256'},
            {'now': get_timestamp() - 610, 'customer_id': 114514},
            Config.SECRET_KEY
        )

        # 检验令牌
        response = self.client.get('/auth/register_confirm?token={}'.format(token.decode()))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(PyQuery(response.text)('.jumbotron .h3').text() == '验证失败，链接已过期')

    def test_fake_token_2(self):
        """令牌检验：伪造数据库中不对应的令牌"""
        # 生成令牌
        token = jwt.encode(
            {'alg': 'HS256'},
            {'now': get_timestamp(), 'customer_id': 114514},
            Config.SECRET_KEY
        )

        # 检验令牌
        response = self.client.get('/auth/register_confirm?token={}'.format(token.decode()))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(PyQuery(response.text)('.jumbotron .h3').text() == '验证失败，无效链接')

    def test_again_verify_token(self):
        """令牌检验：重复验证已注册成功的用户"""
        # 成功注册一个用户
        cus = Customer(
            customer_id=1,
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456',
            confirmed=1
        )
        db.session.add(cus)
        db.session.commit()

        # 生成令牌
        token = jwt.encode(
            {'alg': 'HS256'},
            {'now': get_timestamp(), 'customer_id': 1},
            Config.SECRET_KEY
        )

        # 检验令牌
        response = self.client.get('/auth/register_confirm?token={}'.format(token.decode()))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(PyQuery(response.text)('.jumbotron .h3').text() == '请不要重复进行验证')

    def test_success_verify_token(self):
        """令牌检验：成功验证令牌"""
        # 成功注册一个用户
        cus = Customer(
            customer_id=1,
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456'
        )
        db.session.add(cus)
        db.session.commit()

        # 生成令牌
        token = jwt.encode(
            {'alg': 'HS256'},
            {'now': get_timestamp(), 'customer_id': 1},
            Config.SECRET_KEY
        )

        # 检验令牌
        response = self.client.get('/auth/register_confirm?token={}'.format(token.decode()))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(PyQuery(response.text)('.jumbotron .h3').text() == '验证成功，请到登录页登录')

        # 验证数据库
        self.assertTrue(Customer.query.filter_by(customer_email='2428207444@qq.com').first().confirmed)
