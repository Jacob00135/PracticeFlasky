import unittest
from pyquery import PyQuery
from app import create_app, db
from app.models import Customer


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

    def test_email_exists(self):
        """更改邮箱：邮箱已被注册"""
        # 已被注册的邮箱
        cus = Customer(
            customer_email='2026754775@qq.com',
            customer_name='xie',
            password='123456',
            confirmed=1
        )
        db.session.add(cus)
        db.session.commit()

        # 登录
        response = self.client.post('/auth/login', json={
            'email': '2428207444@qq.com',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

        # 更改邮箱请求
        response = self.client.post('/auth/send_confirm/update_email', json={'email': '2026754775@qq.com'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '该邮箱已被注册')

    def test_update_success(self):
        """更改邮箱：更改成功"""
        cus = Customer.query.filter_by(customer_email='2428207444@qq.com').first()
        response = self.client.get('/auth/update_email_confirm?token={}'.format(cus.generate_confirmation_token({'em': '2026754775@qq.com'}).decode()))
        self.assertTrue(response.status_code == 200)
        self.assertTrue(PyQuery(response.text)('.jumbotron .h3').text() == '验证成功')
        self.assertTrue(Customer.query.filter_by(customer_name='XieJiyue').first().customer_email == '2026754775@qq.com')
