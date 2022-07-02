import unittest
from pyquery import PyQuery
from app import create_app, db
from app.models import Customer


class LoginTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_name='testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        cus = Customer(
            customer_email='flasky@163.com',
            customer_name='flasky',
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
        """登录检查：邮箱不存在"""
        response = self.client.post('/auth/login', json={
            'email': 'test@qq.com',
            'password': '12345'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 0)
        self.assertTrue(result['message'] == '邮箱不存在！')

    def test_no_confirm(self):
        """登录检查：未确认注册用户不予登录"""
        Customer.query.filter_by(customer_email='flasky@163.com').first().confirmed = 0
        response = self.client.post('/auth/login', json={
            'email': 'flasky@163.com',
            'password': '12345'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 0)
        self.assertTrue(result['message'] == '您已注册但邮箱未确认，请重新注册！')

    def test_password_error(self):
        """登录检查：密码不正确"""
        response = self.client.post('/auth/login', json={
            'email': 'flasky@163.com',
            'password': '654321'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 0)
        self.assertTrue(result['message'] == '密码错误！')

    def test_login_success(self):
        """登录检查：登录成功重定向到主页"""
        response = self.client.post('/auth/login', json={
            'email': 'flasky@163.com',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

    def test_login_success_2(self):
        """登录检查：登录成功重定向到原页面"""
        response = self.client.post('/auth/login?next=/customer/update_customer_info/flasky', json={
            'email': 'flasky@163.com',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/customer/update_customer_info/flasky')

    def test_logout(self):
        """登出检查"""
        # 登录
        response = self.client.post('/auth/login', json={
            'email': 'flasky@163.com',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

        # 登出
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(response.history) == 1)
        self.assertTrue(response.history[0].status_code == 302)
        self.assertTrue(response.history[0].location == '/')
        response = self.client.get('/auth/login')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(PyQuery(response.text)('#nav-bar a.login').text() == '登录')
