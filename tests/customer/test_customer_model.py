import unittest
from app.models import db, Customer, Role, Permission, AnonymousCustomer
from app import create_app


class CustomerModelTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app(config_name='testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        """检查密码散列值是否计算成功"""
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456'
        )
        self.assertTrue(cus.password_hash is not None)
        self.assertTrue(cus.password_hash.startswith('pbkdf2:sha256:'))

    def test_password_getter(self):
        """检查是否禁止访问Customer的密码属性"""
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456'
        )
        with self.assertRaises(AttributeError):
            print(cus.password)

    def test_password_verification(self):
        """检查是否可验证密码与散列值的等价"""
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456'
        )
        self.assertTrue(cus.verify_password('123456'))
        self.assertFalse(cus.verify_password('flasky'))

    def test_password_salts_are_random(self):
        """检查计算散列值的盐值是否是随机的"""
        cus1 = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='flasky'
        )
        cus2 = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='flasky'
        )
        cus1.password = 'flasky'
        cus2.password = 'flasky'
        self.assertTrue(cus1.password_hash != cus2.password_hash)

    def test_flask_login_attribute_exists(self):
        """检查Flask-Login要求Customer所拥有的属性是否存在"""
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='flasky'
        )
        self.assertTrue(cus.is_active is not None)
        self.assertTrue(cus.is_authenticated is not None)
        self.assertTrue(cus.is_anonymous is not None)
        self.assertTrue(cus.get_id() == str(cus.customer_id))

    def test_exists_role(self):
        """角色模型：是否存在三种角色"""
        self.assertTrue(len(Role.query.all()) == 3)

        customer = Role.query.filter_by(role_name='Customer').first()
        self.assertTrue(customer is not None)
        self.assertTrue(customer.is_default)
        self.assertTrue(customer.permissions == 7)

        moderator = Role.query.filter_by(role_name='Moderator').first()
        self.assertTrue(moderator is not None)
        self.assertFalse(moderator.is_default)
        self.assertTrue(moderator.permissions == 15)

        administrator = Role.query.filter_by(role_name='Administrator').first()
        self.assertTrue(administrator is not None)
        self.assertFalse(administrator.is_default)
        self.assertTrue(administrator.permissions == 31)

    def test_default_customer(self):
        """用户模型：默认角色是Customer"""
        cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='XieJiyue',
            password='123456'
        )
        db.session.add(cus)
        db.session.commit()
        self.assertTrue(cus.role_id == Role.query.filter_by(role_name='Customer').first().role_id)
        self.assertTrue(cus.can(Permission.FOLLOW))
        self.assertTrue(cus.can(Permission.COMMENT))
        self.assertTrue(cus.can(Permission.WRITE))
        self.assertFalse(cus.can(Permission.MODERATE))
        self.assertFalse(cus.can(Permission.ADMIN))

    def test_default_admin(self):
        """用户模型：默认角色是Administrator"""
        cus = Customer(
            customer_email='flasksender@qq.com',
            customer_name='Flasky Admin',
            password='123456'
        )
        db.session.add(cus)
        db.session.commit()
        self.assertTrue(cus.role_id == Role.query.filter_by(role_name='Administrator').first().role_id)
        self.assertTrue(cus.can(Permission.FOLLOW))
        self.assertTrue(cus.can(Permission.COMMENT))
        self.assertTrue(cus.can(Permission.WRITE))
        self.assertTrue(cus.can(Permission.MODERATE))
        self.assertTrue(cus.can(Permission.ADMIN))

    def test_anonymous_customer(self):
        """用户模型：匿名用户"""
        ac = AnonymousCustomer()
        self.assertFalse(ac.can(Permission.FOLLOW))
        self.assertFalse(ac.can(Permission.COMMENT))
        self.assertFalse(ac.can(Permission.WRITE))
        self.assertFalse(ac.can(Permission.MODERATE))
        self.assertFalse(ac.can(Permission.ADMIN))
