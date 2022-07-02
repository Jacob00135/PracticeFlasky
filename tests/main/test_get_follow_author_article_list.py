import unittest
from datetime import datetime
from app import create_app, db
from app.models import Article, Customer, Role


class GetFollowAuthorArticleListTestCase(unittest.TestCase):
    def setUp(self) -> None:
        # 创建应用
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(True)
        db.create_all()
        Role.insert_roles()

        # 插入测试数据
        self.jacob = Customer(
            customer_id=1,
            customer_email='2428207444@qq.com',
            customer_name='Jacob',
            password='123456',
            role=Role.query.filter_by(role_name='Customer').first(),
            confirmed=1,
            about_me='一名Python工程师'
        )
        self.xiejiyue = Customer(
            customer_id=2,
            customer_email='1466291943@qq.com',
            customer_name='XieJiyue',
            password='123456',
            role=Role.query.filter_by(role_name='Moderator').first(),
            confirmed=1,
            about_me='软件测试员'
        )
        self.admin = Customer(
            customer_id=3,
            customer_email='flasksender@qq.com',
            customer_name='FlaskyAdmin',
            password='123456',
            role=Role.query.filter_by(role_name='Administrator').first(),
            confirmed=1,
            about_me='Flasky管理员'
        )
        record_list = [self.jacob, self.xiejiyue, self.admin]
        title_list = [
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
        for author_id in range(1, 4):
            for title in title_list:
                record_list.append(Article(
                    title=title,
                    content=title,
                    publish_time=datetime.utcnow(),
                    author_id=author_id
                ))
        db.session.add_all(record_list)
        db.session.commit()

        # 计算总文章数量、总页码数、每个用户的文章数量、每个用户的文章页码数
        self.customer_article_count = len(title_list)
        self.article_count = self.customer_article_count * 3
        self.assertTrue(len(Article.query.all()) == self.article_count)

        # 构建关注关系
        self.xiejiyue.follow(self.jacob)
        self.xiejiyue.follow(self.admin)
        self.assertTrue(len(self.xiejiyue.follow_author.all()) == 2)

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_follow_author_articles_attribute(self):
        """检查属性：Customer实例的follow_author_articles"""
        self.assertTrue(len(self.xiejiyue.follow_author_articles.all()) == self.customer_article_count * 2)
