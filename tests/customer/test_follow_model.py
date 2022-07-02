import unittest
from app import create_app, db
from app.models import Customer, Role, Follow


class FollowModelTestCase(unittest.TestCase):

    def setUp(self) -> None:
        # 创建应用
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        Role.insert_roles()

        # 插入测试数据
        self.admin = Customer(
            customer_id=1,
            customer_email='flasksender@qq.com',
            customer_name='FlaskyAdmin',
            password='123456',
            role=Role.query.filter_by(role_name='Administrator').first(),
            confirmed=1,
            about_me='Flasky管理员'
        )
        self.cus_list = []
        for i in range(2, 7):
            self.cus_list.append(Customer(
                customer_id=i,
                customer_email='{}@qq.com'.format(i),
                customer_name='cus_{}'.format(i),
                password='123456',
                role=Role.query.filter_by(role_name='Customer').first(),
                confirmed=1
            ))
        db.session.add_all(self.cus_list)
        db.session.add(self.admin)
        db.session.commit()

        # 检查测试数据是否插入完毕
        self.assertTrue(len(Customer.query.all()) == 6)

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_follow_function(self):
        """follow方法：关注用户"""
        self.cus_list[0].follow(self.admin)
        self.assertTrue(
            Follow.query.filter_by(
                fans_id=self.cus_list[0].customer_id,
                author_id=self.admin.customer_id
            ).first() is not None
        )

    def test_unfollow_function(self):
        """unfollow方法：取消关注用户"""
        self.cus_list[0].follow(self.admin)
        self.assertTrue(
            Follow.query.filter_by(
                fans_id=self.cus_list[0].customer_id,
                author_id=self.admin.customer_id
            ).first() is not None
        )
        self.cus_list[0].unfollow(self.admin)
        self.assertTrue(
            Follow.query.filter_by(
                fans_id=self.cus_list[0].customer_id,
                author_id=self.admin.customer_id
            ).first() is None
        )

    def test_is_following_function(self):
        """is_following方法：是否关注了某用户"""
        self.cus_list[0].follow(self.admin)
        self.assertTrue(
            Follow.query.filter_by(
                fans_id=self.cus_list[0].customer_id,
                author_id=self.admin.customer_id
            ).first() is not None
        )
        self.assertTrue(self.cus_list[0].is_following(self.admin))
        self.assertFalse(self.cus_list[0].is_following(self.cus_list[1]))

    def test_is_fans_function(self):
        """is_fans方法：某用户是否是粉丝"""
        self.cus_list[0].follow(self.admin)
        self.assertTrue(
            Follow.query.filter_by(
                fans_id=self.cus_list[0].customer_id,
                author_id=self.admin.customer_id
            ).first() is not None
        )
        self.assertTrue(self.admin.is_fans(self.cus_list[0]))
        self.assertFalse(self.admin.is_fans(self.cus_list[1]))

    def test_follow_author_attribute(self):
        """follow_author属性：本用户已关注的作者"""
        fans = self.cus_list[0]
        for cus in self.cus_list[1:]:
            fans.follow(cus)
            self.assertTrue(
                Follow.query.filter_by(
                    fans_id=fans.customer_id,
                    author_id=cus.customer_id
                ).first() is not None
            )
        f_list = fans.follow_author.all()
        self.assertTrue(len(f_list) == 4)
        for i in range(4):
            f = f_list[i]
            self.assertTrue(f.fans_id == fans.customer_id)
            self.assertTrue(f.author_id == self.cus_list[i + 1].customer_id)

    def test_fans_attribute(self):
        """fans属性：本用户的粉丝"""
        for cus in self.cus_list:
            cus.follow(self.admin)
            self.assertTrue(
                Follow.query.filter_by(
                    fans_id=cus.customer_id,
                    author_id=self.admin.customer_id
                ).first() is not None
            )
        f_list = self.admin.fans.all()
        self.assertTrue(len(f_list) == 5)
        for i in range(5):
            f = f_list[i]
            self.assertTrue(f.fans_id == self.cus_list[i].customer_id)
            self.assertTrue(f.author_id == self.admin.customer_id)

    def test_not_allow_follow_self(self):
        """不允许关注自己"""
        self.admin.follow(self.admin)
        self.assertTrue(
            Follow.query.filter_by(
                fans_id=self.admin.customer_id,
                author_id=self.admin.customer_id
            ).first() is None
        )
