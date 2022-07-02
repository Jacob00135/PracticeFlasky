import unittest
from flask import current_app
from app import create_app, db
from app.models import Role, Customer


class BasicsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_name='testing')
        self.app_context = self.app.app_context()
        self.client = self.app.test_client(True)
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        admin = Customer(
            customer_email='flasksender@qq.com',
            customer_name='Flasky Admin',
            password='001358cacab',
            about_me='',
            confirmed=1,
        )
        db.session.add(admin)
        db.session.commit()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        """检查应用是否启动成功"""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """检查应用是否处于测试状态"""
        self.assertTrue(current_app.config['TESTING'])

    def test_have_admin(self):
        """检查应用是否有管理员"""
        admin = Customer.query.filter_by(customer_name='Flasky Admin').first()
        self.assertTrue(admin.role.role_name == 'Administrator')

