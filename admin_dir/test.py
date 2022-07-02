"""from random import randint
from datetime import datetime


def shuffle(ls):
    length = len(ls)
    for i in range(length * 100):
        i = randint(0, length - 1)
        j = randint(0, length - 1)
        t = ls[i]
        ls[i] = ls[j]
        ls[j] = t
    return ls


title_list = shuffle([
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
])
cus_list = Customer.query.all()
article_list = []
for cus in cus_list:
    for title in title_list:
        for i in range(10):
            article_list.append(Article(
                title=title,
                content=title,
                publish_time=datetime.utcnow(),
                author_id=cus.customer_id
            ))
db.session.add_all(article_list)
db.session.commit()"""

"""from random import randint
from datetime import datetime
from time import sleep


def shuffle(ls):
    length = len(ls)
    for i in range(length * 100):
        i = randint(0, length - 1)
        j = randint(0, length - 1)
        t = ls[i]
        ls[i] = ls[j]
        ls[j] = t
    return ls


title_list = shuffle([
    'Jacob',
    # 'XieJiyue',
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
])
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

xiejiyue = Customer.query.filter_by(customer_name='XieJiyue').first()
for cus in Customer.query.all():
    sleep(0.1)
    xiejiyue.follow(cus)

jacob = Customer.query.filter_by(customer_name='Jacob').first()
for cus in Customer.query.all():
    sleep(0.1)
    cus.follow(jacob)"""

"""from random import randint
from datetime import datetime
from time import sleep


def shuffle(ls):
    length = len(ls)
    for i in range(length * 100):
        i = randint(0, length - 1)
        j = randint(0, length - 1)
        t = ls[i]
        ls[i] = ls[j]
        ls[j] = t
    return ls


title_list = shuffle([
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
])
cus_list = []
xiejiyue = Customer.query.filter_by(customer_name='XieJiyue').first()
for title in title_list:
    cus_list.append(Comment(
        content=title,
        comment_time=datetime.utcnow(),
        author_id=xiejiyue.customer_id,
        article_id=3322
    ))
db.session.add_all(cus_list)
db.session.commit()"""