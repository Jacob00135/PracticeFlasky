import unittest
from app import create_app
from app.models import db, Customer, Role


class CustomerInfoTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        Role.insert_roles()
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='Jacob',
            password='123456',
            role=Role.query.filter_by(role_name='Customer').first(),
            confirmed=1,
            about_me='一名Python工程师'
        )
        moderator = Customer(
            customer_email='1466291943@qq.com',
            customer_name='XieJiyue',
            password='123456',
            role=Role.query.filter_by(role_name='Moderator').first(),
            confirmed=1,
            about_me='软件测试员'
        )
        admin = Customer(
            customer_email='flasksender@qq.com',
            customer_name='FlaskyAdmin',
            password='123456',
            role=Role.query.filter_by(role_name='Administrator').first(),
            confirmed=1,
            about_me='Flasky管理员'
        )
        db.session.add_all([cus, moderator, admin])
        db.session.commit()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_anonymous_customer(self):
        """游客访问用户资料页面"""
        # 访问普通用户的个人资料页面
        response = self.client.get('/customer/Jacob')
        self.assertTrue(response.status_code == 200)

        # 访问协管员的个人资料页面
        response = self.client.get('/customer/XieJiyue')
        self.assertTrue(response.status_code == 200)

        # 访问管理员的个人资料页面
        self.assertTrue(self.client.get('/customer/FlaskyAdmin').status_code == 403)

    def test_customer(self):
        """普通用户访问用户资料页面"""
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

        # 访问自己的个人资料页面
        response = self.client.get('/customer/Jacob')
        self.assertTrue(response.status_code == 200)

        # 访问别人的个人资料页面
        response = self.client.get('/customer/XieJiyue')
        self.assertTrue(response.status_code == 200)

        # 访问管理员的个人资料页面
        self.assertTrue(self.client.get('/customer/FlaskyAdmin').status_code == 403)

        # 访问自己的修改信息页面
        response = self.client.get('/customer/update_customer_info/Jacob')
        self.assertTrue(response.status_code == 200)

        # 访问别人的修改信息页面
        self.assertTrue(self.client.get('/customer/update_customer_info/XieJiyue').status_code == 403)
        self.assertTrue(self.client.get('/customer/update_customer_info/FlaskyAdmin').status_code == 403)

    def test_moderator(self):
        """协管员访问用户资料页面"""
        # 登录
        response = self.client.post('/auth/login', json={
            'email': '1466291943@qq.com',
            'password': '123456'
        }, follow_redirects=True)
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

        # 访问自己的个人资料页面
        response = self.client.get('/customer/XieJiyue')
        self.assertTrue(response.status_code == 200)

        # 访问别人的个人资料页面
        response = self.client.get('/customer/Jacob')
        self.assertTrue(response.status_code == 200)

        # 访问管理员的个人资料页面
        self.assertTrue(self.client.get('/customer/FlaskyAdmin').status_code == 403)

        # 访问自己的修改信息页面
        response = self.client.get('/customer/update_customer_info/XieJiyue')
        self.assertTrue(response.status_code == 200)

        # 访问别人的修改信息页面
        self.assertTrue(self.client.get('/customer/update_customer_info/Jacob').status_code == 403)
        self.assertTrue(self.client.get('/customer/update_customer_info/FlaskyAdmin').status_code == 403)

    def test_administrator(self):
        """管理员访问用户资料页面"""
        # 登录
        response = self.client.post('/auth/login', json={
            'email': 'flasksender@qq.com',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

        # 访问自己的个人资料页面
        response = self.client.get('/customer/FlaskyAdmin')
        self.assertTrue(response.status_code == 200)

        # 访问别人的个人资料页面
        response = self.client.get('/customer/Jacob')
        self.assertTrue(response.status_code == 200)

        # 访问自己的修改信息页面
        response = self.client.get('/customer/update_customer_info/FlaskyAdmin')
        self.assertTrue(response.status_code == 200)

        # 访问别人的修改信息页面
        response = self.client.get('/customer/update_customer_info/Jacob')
        self.assertTrue(response.status_code == 200)

    def test_customer_update_info(self):
        """普通用户修改信息"""
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

        # 修改别人的信息
        self.assertTrue(self.client.post('/customer/update_customer_info/XieJiyue').status_code == 403)

        # 修改信息：用户名重复
        response = self.client.post('/customer/update_customer_info/Jacob', json={
            'customer-name': 'XieJiyue',
            'description': '一名Java工程师'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '用户名已存在！')

        # 修改信息：修改成功
        response = self.client.post('/customer/update_customer_info/Jacob', json={
            'customer-name': 'Jacob2',
            'description': '一名Java工程师'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '修改成功，即将跳转到个人资料页面')
        cus = Customer.query.filter_by(customer_email='2428207444@qq.com').first()
        self.assertTrue(cus.customer_name == 'Jacob2')
        self.assertTrue(cus.about_me == '一名Java工程师')

    def test_admin_update_info(self):
        """管理员修改信息"""
        # 登录
        response = self.client.post('/auth/login', json={
            'email': 'flasksender@qq.com',
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

        # 修改信息：要修改的用户不存在
        response = self.client.post('/customer/update_customer_info/test')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '要修改的用户不存在！')

        # 修改信息：用户名重复
        response = self.client.post('/customer/update_customer_info/Jacob', json={
            'customer-name': 'XieJiyue',
            'description': '一名Java工程师'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '用户名已存在！')

        # 修改信息：邮箱已被注册
        response = self.client.post('/customer/update_customer_info/Jacob', json={
            'customer-name': 'Jacob',
            'description': '一名Java工程师',
            'email': '1466291943@qq.com'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '邮箱已被注册！')

        # 修改信息：用户身份不存在
        response = self.client.post('/customer/update_customer_info/Jacob', json={
            'customer-name': 'Jacob',
            'description': '一名Java工程师',
            'email': '2428207444@qq.com',
            'role-name': 'hack'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '不存在这个用户身份！')

        # 修改信息：成功修改
        response = self.client.post('/customer/update_customer_info/Jacob', json={
            'customer-name': 'Jacob2',
            'description': '一名Java工程师',
            'email': 'test@qq.com',
            'role-name': 'Moderator'
        })
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '修改成功，即将跳转到个人资料页面')
        self.assertTrue(Customer.query.filter_by(customer_name='Jacob').first() is None)
        cus = Customer.query.filter_by(customer_name='Jacob2').first()
        self.assertTrue(cus.about_me == '一名Java工程师')
        self.assertTrue(cus.customer_email == 'test@qq.com')
        self.assertTrue(cus.role.role_name == 'Moderator')
