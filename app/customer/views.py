import os.path
import imghdr
from flask import render_template, abort, request
from flask_login import current_user, login_required
from . import customer
from ..common_function import get_md5_encode
from ..models import db, Customer, Role, Permission, Follow, Article
from ..decorators import permission_required
from config import Config


@customer.route('/<customer_name>')
def customer_page(customer_name):
    cus = Customer.query.filter_by(customer_name=customer_name).first_or_404()

    # 当前用户拥有管理员权限，才能访问管理员的个人资料页面，否则响应403
    if not current_user.is_administrator() and cus.is_administrator():
        abort(403)

    # 查询数据库中的文章列表
    bq = Article.query.filter_by(author_id=cus.customer_id).order_by(Article.publish_time.desc())

    # 获取符合条件的记录总个数，计算页数
    page_count = bq.count() / Config.FLASKY_MAX_ARTICLE_NUMBER
    if page_count > int(page_count):
        page_count = int(page_count) + 1
    else:
        page_count = int(page_count)

    # 获取当前页的条目
    page = request.args.get('page', 1, type=int)
    if page < 1 or page > page_count:
        page = 1
    article_list = bq.paginate(
        page,
        per_page=Config.FLASKY_MAX_ARTICLE_NUMBER,
        error_out=False
    ).items

    return render_template('customer/index.html', cus=cus, article_list=article_list, page_count=page_count, current_page=page)


@customer.route('/get_description')
def get_description():
    # 检查参数是否合理
    customer_name = request.args.get('customer_name')
    if customer_name is None:
        return {'status': 0, 'message': '必须提供用户名！'}
    cus = Customer.query.filter_by(customer_name=customer_name).first()
    if cus is None:
        return {'status': 0, 'message': '用户不存在！'}

    # 当简介为空时，返回“无”
    description = cus.about_me
    if not description:
        description = '无'

    return {'status': 1, 'message': '获取成功', 'description': description}


@customer.route('/update_customer_info/<customer_name>', methods=['GET', 'POST'])
@login_required
def update_customer_info(customer_name):
    if request.method == 'GET':
        update_customer = Customer.query.filter_by(customer_name=customer_name).first_or_404()
        if not current_user.is_administrator():
            if current_user.customer_name != customer_name:
                abort(403)
            return render_template('customer/update-info.html', cus=current_user)
        return render_template('customer/update-info.html', cus=update_customer)
    elif request.method == 'POST':
        # 确定要修改哪个用户
        if current_user.is_administrator():
            update_customer = Customer.query.filter_by(customer_name=customer_name).first()
            if update_customer is None:
                return {'status': 0, 'message': '要修改的用户不存在！'}
        else:
            if current_user.customer_name != customer_name:
                abort(403)
            update_customer = current_user

        data = request.json

        # 非管理员修改信息，只对用户名、个人简介作修改
        if update_customer.customer_name != data['customer-name'] and \
                Customer.query.filter_by(customer_name=data['customer-name']).first() is not None:
            return {'status': 0, 'message': '用户名已存在！'}
        update_customer.customer_name = data['customer-name']
        if not data['description']:
            update_customer.about_me = None
        else:
            update_customer.about_me = data['description']
        if not current_user.is_administrator():
            db.session.add(update_customer)
            db.session.commit()
            return {'status': 1, 'message': '修改成功，即将跳转到个人资料页面'}

        # 管理员修改信息，还要检查邮箱、用户身份
        customer_email = data['email']
        if update_customer.customer_email != customer_email and Customer.query.filter_by(customer_email=customer_email).first() is not None:
            return {'status': 0, 'message': '邮箱已被注册！'}
        update_customer.update_customer_email(customer_email)
        role = Role.query.filter_by(role_name=data['role-name']).first()
        if role is None:
            return {'status': 0, 'message': '不存在这个用户身份！'}
        update_customer.role = role
        db.session.add(update_customer)
        db.session.commit()

        return {'status': 1, 'message': '修改成功，即将跳转到个人资料页面'}


@customer.route('/update_head_portrait/<customer_name>', methods=['POST'])
@login_required
def update_head_portrait(customer_name):
    # 检查权限
    cus = Customer.query.filter_by(customer_name=customer_name).first()
    if cus is None:
        return {'status': 0, 'message': '用户不存在！'}
    if not current_user.is_administrator() and current_user.customer_name != customer_name:
        return {'status': 0, 'message': '无效用户名'}

    # 检查图片类型
    img = request.files['head_portrait']
    extension_name = img.filename.split('.')[-1]
    img_type = imghdr.what(img)
    if extension_name not in ['jpg', 'jpeg', 'png'] or img.mimetype not in ['image/jpeg', 'image/png', 'image/webp'] or img_type not in ['jpeg', 'png', 'webp']:
        return {'status': 0, 'message': '不支持的头像图片类型'}

    # 保存图片并指定用户的头像
    filename = get_md5_encode(cus.customer_email) + '.' + extension_name
    cus.update_head_portrait(filename)
    img.save(os.path.join(Config.HEAD_PORTRAIT_PATH, filename))
    db.session.add(cus)
    db.session.commit()

    return {'status': 1, 'message': '更改头像成功，即将刷新页面'}


@customer.route('/follow', methods=['POST'])
@permission_required(Permission.FOLLOW)
def follow():
    # 检查用户名
    customer_name = request.json['customer-name']
    cus = Customer.query.filter_by(customer_name=customer_name).first()
    if cus is None:
        return {'status': 0, 'message': '要关注的用户不存在！'}

    # 关注用户
    current_user.follow(cus)
    return {'status': 1, 'message': '关注成功'}


@customer.route('/unfollow', methods=['POST'])
@permission_required(Permission.FOLLOW)
def unfollow():
    # 检查用户名
    customer_name = request.json['customer-name']
    cus = Customer.query.filter_by(customer_name=customer_name).first()
    if cus is None:
        return {'status': 0, 'message': '要取消关注的用户不存在！'}

    # 关注用户
    current_user.unfollow(cus)
    return {'status': 1, 'message': '取消关注成功'}


@customer.route('/follow_author/<customer_name>')
def show_follow_author(customer_name):
    # 获取参数
    cus = Customer.query.filter_by(customer_name=customer_name).first_or_404()
    page = request.args.get('page', 1, type=int)

    # 查询数据库
    bq = cus.follow_author.order_by(Follow.follow_time.desc())

    # 获取符合条件的记录总个数，计算页数
    page_count = bq.count() / Config.FLASKY_MAX_CUSTOMER_NUMBER
    if page_count > int(page_count):
        page_count = int(page_count) + 1
    else:
        page_count = int(page_count)
    follow_author_list = bq.paginate(page, per_page=Config.FLASKY_MAX_CUSTOMER_NUMBER, error_out=False).items

    return render_template(
        'customer/follow-author-list.html',
        cus=cus,
        follow_list=follow_author_list,
        current_page=page,
        page_count=page_count
    )


@customer.route('/fans/<customer_name>')
def show_fans(customer_name):
    # 获取参数
    cus = Customer.query.filter_by(customer_name=customer_name).first_or_404()
    page = request.args.get('page', 1, type=int)

    # 查询数据库
    bq = cus.fans.order_by(Follow.follow_time.desc())

    # 获取符合条件的记录总个数，计算页数
    page_count = bq.count() / Config.FLASKY_MAX_CUSTOMER_NUMBER
    if page_count > int(page_count):
        page_count = int(page_count) + 1
    else:
        page_count = int(page_count)
    fans_list = bq.paginate(page, per_page=Config.FLASKY_MAX_CUSTOMER_NUMBER, error_out=False).items

    return render_template(
        'customer/fans-list.html',
        cus=cus,
        follow_list=fans_list,
        current_page=page,
        page_count=page_count
    )
