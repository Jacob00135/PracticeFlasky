import unittest
from app import create_app, db
from app.models import Customer


class ForgetPasswordTestCase(unittest.TestCase):
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

    def test_not_exists_email(self):
        """忘记密码：邮箱不存在"""
        response = self.client.post('/auth/send_confirm/forget_password', json={
            'email': '123456@qq.com',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '该邮箱未注册')

    def test_not_confirm(self):
        """忘记密码：未确认的邮箱"""
        Customer.query.filter_by(customer_email='2428207444@qq.com').first().confirmed = 0
        response = self.client.post('/auth/send_confirm/forget_password', json={
            'email': '2428207444@qq.com',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '您已注册但邮箱未确认，请重新注册！')

    def test_same_password(self):
        """忘记密码：新旧密码一样"""
        response = self.client.post('/auth/send_confirm/forget_password', json={
            'email': '2428207444@qq.com',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '新密码不能与旧密码一样！')
