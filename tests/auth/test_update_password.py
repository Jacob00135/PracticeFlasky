import unittest
from time import time as get_timestamp
from pyquery import PyQuery
from werkzeug.security import generate_password_hash
from authlib.jose import jwt
from app import create_app, db
from app.models import Customer
from config import Config


class UpdatePasswordTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_name='testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456',
            confirmed=1
        )
        db.session.add(cus)
        db.session.commit()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_same_password(self):
        """修改密码：新旧密码一样"""
        # 登录
        response = self.client.post('/auth/login', json={'email': '2428207444@qq.com', 'password': '123456'})
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

        # 修改密码
        response = self.client.post('/auth/send_confirm/update_password', json={'password': '123456'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '新密码不能与旧密码一样')

    def test_send_success(self):
        """修改密码：发送确认邮件成功"""
        # 登录
        response = self.client.post('/auth/login', json={'email': '2428207444@qq.com', 'password': '123456'})
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

        # 修改密码
        response = self.client.post('/auth/send_confirm/update_password', json={'password': '78901'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '确认邮件已发送至邮箱，请前往确认')

    def test_update_success(self):
        """修改密码成功"""
        # 登录
        response = self.client.post('/auth/login', json={'email': '2428207444@qq.com', 'password': '123456'})
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

        # 修改密码
        response = self.client.get('/auth/update_password_confirm?token={}'.format(jwt.encode(
            {'alg': 'HS256'},
            {
                'now': get_timestamp(),
                'customer_id': Customer.query.filter_by(customer_email='2428207444@qq.com').first().customer_id,
                'psw': generate_password_hash('78901')
            },
            Config.SECRET_KEY
        ).decode()))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(PyQuery(response.text)('.jumbotron .h3').text() == '验证成功')

        # 检查密码是否已经更改成功
        self.assertTrue(Customer.query.filter_by(customer_email='2428207444@qq.com').first().verify_password('78901'))
