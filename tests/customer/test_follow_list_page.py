import unittest
from datetime import datetime
from app import create_app, db
from app.models import Customer, Role, Follow


class FollowListPageTestCase(unittest.TestCase):

    def setUp(self) -> None:
        # 创建应用
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        Role.insert_roles()

        # 插入测试数据
        title_list = [
            'Jacob',
            'XieJiyue',
            '神经网络与深度学习',
            'PyCharm的操作方式',
            'TensorFlow2.0安装教程',
            'SQL注入攻击与防范',
            'CSRF攻击简介',
            'Python爬虫技术',
            'Flask框架的一些bug',
            'Flasky的安全性改善',
            '各大前端框架对比',
            '面向对象思想',
            'Python装饰器与生成器的区别',
            'Python数据可视化',
            '基于深度学习的图像识别',
            '手写数字识别教程',
            'Django VS Flask',
            '归并排序介绍',
            '[数据结构]二叉树与平衡二叉树',
            '为什么0.1+0.2不等于0.3？',
            '宇宙最强IDE：PyCharm',
            'HTML5真的能代替PHP吗？',
            '元胞自动机与图灵机',
            '车载系统中的不良驾驶行为检测',
            '深度学习-图片对抗',
            '梯度下降法与深度学习优化器',
            '浅谈Flask开发模式：MVT设计模式',
            '为什么pymysql库的使用方法如此古老？',
            '基础bash命令学习',
            'Flask数据库迁移扩展中遇到的坑',
            'Typora使用教程',
            'SPSS数据分析',
            '滑动验证码的破解方法',
            '计算机网络安全：DDOS攻击',
            '2022年4月热门编程语言排行榜',
            'Hadoop分布式大数据平台的搭建',
            '基础Linux命令',
            '渲染HTML使用JinJa2还是js？'
        ]
        self.customer_count = len(title_list)
        cus_list = []
        for i, title in enumerate(title_list):
            cus_list.append(Customer(
                customer_email='{}@qq.com'.format(i),
                customer_name=title,
                password='123456',
                role_id=Role.query.filter_by(role_name='Customer').first().role_id,
                confirmed=1,
                about_me=title,
                member_since=datetime.utcnow(),
                last_seen=datetime.utcnow()
            ))
        db.session.add_all(cus_list)
        db.session.commit()

        # XieJiyue关注所有用户
        xiejiyue = Customer.query.filter_by(customer_name='XieJiyue').first()
        for cus in Customer.query.all():
            xiejiyue.follow(cus)

        # Jacob被所有用户关注
        jacob = Customer.query.filter_by(customer_name='Jacob').first()
        for cus in Customer.query.all():
            cus.follow(jacob)

        # 检查测试数据是否插入完毕
        self.assertTrue(len(Customer.query.all()) == 38)
        self.assertTrue(len(xiejiyue.follow_author.all()) == 37)
        self.assertTrue(len(jacob.fans.all()) == 37)

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, cus):
        response = self.client.post('/auth/login', json={'email': cus.customer_email, 'password': '123456'})
        self.assertTrue(response.status_code == 200)
        result = response.json
        self.assertTrue(result['status'] == 1)
        self.assertTrue(result['message'] == '登录成功')
        self.assertTrue(result['next'] == '/')

    def test_follow_button(self):
        """关注按钮"""
        # 登录
        self.login(Customer.query.filter_by(customer_name='Jacob').first())

        # 关注
        response = self.client.post('/customer/follow', json={'customer-name': 'XieJiyue'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '关注成功')

        # 检查
        xiejiyue_id = Customer.query.filter_by(customer_name='XieJiyue').first().customer_id
        jacob_id = Customer.query.filter_by(customer_name='Jacob').first().customer_id
        self.assertTrue(Follow.query.filter_by(fans_id=jacob_id, author_id=xiejiyue_id).first() is not None)

    def test_unfollow_button(self):
        """取消关注按钮"""
        # 登录
        self.login(Customer.query.filter_by(customer_name='XieJiyue').first())

        # 取消关注
        response = self.client.post('/customer/unfollow', json={'customer-name': 'Jacob'})
        self.assertTrue(response.status_code == 200)
        self.assertTrue(response.json['status'] == 1)
        self.assertTrue(response.json['message'] == '取消关注成功')

        # 检查
        xiejiyue_id = Customer.query.filter_by(customer_name='XieJiyue').first().customer_id
        jacob_id = Customer.query.filter_by(customer_name='Jacob').first().customer_id
        self.assertTrue(Follow.query.filter_by(fans_id=xiejiyue_id, author_id=jacob_id).first() is None)
