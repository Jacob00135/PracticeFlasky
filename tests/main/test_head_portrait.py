import os.path
import unittest
from shutil import copyfile
from app import create_app
from app.models import db, Customer, Role
from config import Config, BASE_DIR, DEFAULT_HEAD_PORTRAIT

"""测试内容
一、以普通用户身份
1.需要修改头像的用户不存在
2.企图修改别人的头像
3.默认头像情况下，修改头像成功，检查：
  --数据库中的邮箱可以对应上头像文件名(md5映射)
  --数据库中的指定的头像文件存在
4.非默认头像情况下，修改头像成功，检查：
  --数据库中的邮箱可以对应上头像文件名(md5映射)
  --数据库中的指定的头像文件存在
5.默认头像情况下，更改邮箱之后，检查：
  --数据库中的邮箱可以对应上头像文件名(md5映射)
  --数据库中的指定的头像文件存在
6.非默认头像情况下，更改邮箱之后，检查：
  --数据库中的邮箱可以对应上头像文件名(md5映射)
  --数据库中的指定的头像文件存在

二、以管理员身份
1.需要修改头像的用户不存在
2.默认头像情况下，修改别人头像成功，检查：
  --数据库中的邮箱可以对应上头像文件名(md5映射)
  --数据库中的指定的头像文件存在
3.非默认头像情况下，，修改别人头像成功，检查：
  --数据库中的邮箱可以对应上头像文件名(md5映射)
  --数据库中的指定的头像文件存在
4.默认头像情况下，在更改信息页面更改邮箱之后，检查：
  --数据库中的邮箱可以对应上头像文件名(md5映射)
  --数据库中的指定的头像文件存在
5.非默认头像情况下，在更改信息页面更改邮箱之后，检查：
  --数据库中的邮箱可以对应上头像文件名(md5映射)
  --数据库中的指定的头像文件存在"""


class HeadPortraitTestCast(unittest.TestCase):
    test_data_path = os.path.join(BASE_DIR, 'tests/test_data')
    test_filename = [DEFAULT_HEAD_PORTRAIT, 'butterfly.jpg', 'Alukard.jpg']

    def setUp(self) -> None:
        # 设置头像缓存路径、检查测试用的头像是否存在
        Config.HEAD_PORTRAIT_PATH = os.path.join(self.test_data_path, 'head_portrait')
        if not os.path.exists(self.test_data_path) or not os.path.exists(Config.HEAD_PORTRAIT_PATH):
            raise FileNotFoundError('头像缓存路径不存在')
        test_file_path = []
        for filename in self.test_filename:
            file_path = os.path.join(self.test_data_path, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError('测试文件不存在：{}'.format(filename))
            test_file_path.append(file_path)
        for i in range(len(self.test_filename)):
            copyfile(test_file_path[i], os.path.join(Config.HEAD_PORTRAIT_PATH, self.test_filename[i]))

        # 创建应用
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        Role.insert_roles()
        self.cus = Customer(
            customer_email='2428207444@qq.com',
            customer_name='Jacob',
            password='123456',
            role=Role.query.filter_by(role_name='Customer').first(),
            confirmed=1,
            about_me='一名Python工程师'
        )
        self.moderator = Customer(
            customer_email='1466291943@qq.com',
            customer_name='XieJiyue',
            password='123456',
            role=Role.query.filter_by(role_name='Moderator').first(),
            confirmed=1,
            about_me='软件测试员'
        )
        self.admin = Customer(
            customer_email='flasksender@qq.com',
            customer_name='FlaskyAdmin',
            password='123456',
            role=Role.query.filter_by(role_name='Administrator').first(),
            confirmed=1,
            about_me='Flasky管理员'
        )
        db.session.add_all([self.cus, self.moderator, self.admin])
        db.session.commit()

    def tearDown(self) -> None:
        for filename in self.test_filename:
            file_path = os.path.join(Config.HEAD_PORTRAIT_PATH, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, cus):
        # 登录
        response = self.client.post('/auth/login', json={
            'email': cus.customer_email,
            'password': '123456'
        })
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

    def test_customer_not_exists(self):
        """修改头像：用户不存在"""
        self.login(self.cus)
        response = self.client.post('/customer/update_head_portrait/test_user')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '用户不存在！')

    def test_update_other(self):
        """修改头像：无权修改别人的头像"""
        self.login(self.cus)
        response = self.client.post('/customer/update_head_portrait/XieJiyue')
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 0)
        self.assertTrue(response.json['message'] == '无效用户名')
