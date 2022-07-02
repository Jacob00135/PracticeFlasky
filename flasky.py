import os
import sys
import click
from app import create_app, db, mail
from app.models import Role, Customer, Permission, Article, Follow, Comment
from config import BASE_DIR

COV = None
if os.environ.get('FLASK_COVERAGE') == '1':
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db,
        mail=mail,
        Role=Role,
        Customer=Customer,
        Permission=Permission,
        Article=Article,
        Follow=Follow,
        Comment=Comment
    )


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='运行测试并获取测试覆盖率报告')
def test(coverage):
    """单元测试"""

    # 是否获取测试覆盖率报告
    if coverage and os.environ.get('FLASK_COVERAGE') != '1':
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + [sys.argv[0] + '.exe'] + sys.argv[1:])

    # 单元测试
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    # 测试覆盖率报告
    if COV is not None:
        COV.stop()
        COV.save()
        print('单元测试覆盖率报告：')
        COV.report()
        html_coverage_dir = os.path.join(BASE_DIR, 'tests/coverage')
        COV.html_report(directory=html_coverage_dir)
        print('HTML 版本的报告：file:///{}/index.html'.format(html_coverage_dir))
        COV.erase()


@app.cli.command()
def deploy():
    # 创建数据库中的所有表
    if len(db.get_tables_for_bind()) == 0:
        db.create_all()

    # 插入用户身份
    Role.insert_roles()

    # 插入管理员记录
    admin = Customer.query.filter_by(customer_email='flasksender@qq.com').first()
    if admin is None:
        admin = Customer(
            customer_email='flasksender@qq.com',
            customer_name='Flasky Admin',
            password='001358cacab',
            about_me='',
            confirmed=1,
        )
        db.session.add(admin)
        db.session.commit()
