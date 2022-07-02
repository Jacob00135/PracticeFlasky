from datetime import datetime
from werkzeug.security import generate_password_hash
from flask import render_template, request, redirect, url_for
from flask_login import login_user, current_user, login_required, logout_user
from smtplib import SMTPDataError
from . import auth
from .auth_function import check_token
from .. import db
from ..models import Customer
from ..flasky_email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_seen()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # GET
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return render_template('auth/login.html')

    # POST
    if current_user.is_authenticated:
        return {'status': 0, 'message': '不可重复登录'}
    data = request.json
    cus = Customer.query.filter_by(customer_email=data['email']).first()
    if cus is None:
        return {'status': 0, 'message': '邮箱不存在！'}
    if not cus.confirmed:
        return {'status': 0, 'message': '您已注册但邮箱未确认，请重新注册！'}
    if not cus.verify_password(data['password']):
        return {'status': 0, 'message': '密码错误！'}
    login_user(cus, True)
    next_route = request.args.get('next', '/', type=str)
    if not next_route.startswith('/'):
        next_route = '/'
    return {'status': 1, 'message': '登录成功', 'next': next_route}


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # 检查是否是已登录状态，若是则重定向到首页
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        return render_template('auth/register.html')
    elif request.method == 'POST':
        # 检查是否是已登录状态，若是则不允许做任何操作
        if current_user.is_authenticated:
            return {'message': '请先登出'}

        # 数据验证
        data = request.json
        customer_name = data['customer-name']
        length = len(customer_name)
        if length == 0 or length > 20:
            return {'status': 0, 'message': '用户名长度不能为空、不能大于20！'}
        password = data['password']
        length = len(password)
        if length < 6 or length > 20:
            return {'status': 0, 'message': '密码长度必须在[6, 20]之间！'}

        # 检查数据库中是否已有相同的邮箱
        cus = Customer.query.filter_by(customer_email=data['email']).first()
        if cus is not None:
            if cus.confirmed:
                # 数据库中已有相同的邮箱，且已经过确认注册
                return {'status': 0, 'message': '邮箱已被注册'}

            # 数据库中已有相同的邮箱，但没有经过确认注册
            cus_same_name = Customer.query.filter_by(customer_name=data['customer-name']).first()

            # 检查注册的用户名是否可能重复
            if cus_same_name is None or data['customer-name'] == cus.customer_name:
                # 用户名不重复，删除旧的记录，插入新的记录
                db.session.delete(cus)
                db.session.commit()
                cus = Customer(
                    customer_email=data['email'],
                    customer_name=data['customer-name'],
                    password=data['password']
                )
                db.session.add(cus)
                db.session.commit()

                # 发送确认邮件
                try:
                    send_email(
                        data['email'],
                        '注册确认',
                        'auth/register_confirm',
                        customer_name=data['customer-name'],
                        confirm_link=url_for('auth.register_confirm', token=cus.generate_confirmation_token(), _external=True)
                    )
                except SMTPDataError:
                    # 发送邮件失败，表明邮箱是无效的
                    db.session.delete(cus)
                    db.session.commit()
                    return {'status': 0, 'message': '邮箱无效，请确认填写正确'}
                return {'status': 1, 'message': '确认邮件已发送至邮箱，请前往确认'}
            return {'status': 0, 'message': '用户名已存在'}
        elif Customer.query.filter_by(customer_name=data['customer-name']).first() is not None:
            # 数据库中没有相同的邮箱，但是有相同的用户名
            return {'status': 0, 'message': '用户名已存在'}
        # 数据库中既没有相同的邮箱，也没有相同的用户名，则添加新用户到数据库
        cus = Customer(
            customer_email=data['email'],
            customer_name=data['customer-name'],
            password=data['password'],
            member_since=datetime.utcnow()
        )
        db.session.add(cus)
        db.session.commit()

        # 发送确认邮件
        try:
            send_email(
                data['email'],
                '注册确认',
                'auth/register_confirm',
                customer_name=cus.customer_name,
                confirm_link=url_for('auth.register_confirm', token=cus.generate_confirmation_token(), _external=True)
            )
        except SMTPDataError:
            # 发送邮件失败，表明邮箱是无效的
            db.session.delete(cus)
            db.session.commit()
            return {'status': 0, 'message': '邮箱无效，请确认填写正确'}
        return {'status': 1, 'message': '确认邮件已发送至邮箱，请前往确认'}


@auth.route('/send_confirm/register', methods=['POST'])
def send_confirm_register():
    email = request.json['email']
    cus = Customer.query.filter_by(customer_email=email).first()
    if cus is None:
        return {'status': 0, 'message': '邮件发送失败，请检查邮箱是否填写正确'}
    if cus.confirmed:
        return {'status': 0, 'message': '该邮件已确认注册，请前往登录页面'}
    send_email(
        email,
        '注册确认',
        'auth/register_confirm',
        customer_name=cus.customer_name,
        confirm_link=url_for('auth.register_confirm', token=cus.generate_confirmation_token(), _external=True)
    )
    return {'status': 1, 'message': '再次发送邮件成功，请前往邮箱确认'}


@auth.route('/register_confirm')
def register_confirm():
    result = check_token(request.args.get('token'))
    if not result['status']:
        return result['response']
    cus = result['cus']
    if cus.confirmed:
        return render_template('auth/confirm.html', info='请不要重复进行验证', info_type='error')
    cus.confirmed = True
    cus.member_since = datetime.utcnow()
    db.session.add(cus)
    db.session.commit()
    return render_template('auth/confirm.html', info='验证成功，请到登录页登录', info_type='hint')


@auth.route('/update_password')
@login_required
def update_password():
    return render_template('/auth/update-password.html')


@auth.route('/update_password_confirm')
def update_password_confirm():
    result = check_token(request.args.get('token'))
    if not result['status']:
        return result['response']
    data = result['data']
    cus = result['cus']
    cus.password_hash = data['psw']
    db.session.add(cus)
    db.session.commit()
    return render_template('auth/confirm.html', info='验证成功', info_type='hint')


@auth.route('/send_confirm/update_password', methods=['POST'])
@login_required
def send_confirm_update_password():
    data = request.json

    # 检查新密码是否与旧密码一样
    if current_user.verify_password(data['password']):
        return {'status': 0, 'message': '新密码不能与旧密码一样'}

    # 发送邮件
    try:
        send_email(
            current_user.customer_email,
            '修改密码',
            'auth/update_password_confirm',
            customer_name=current_user.customer_name,
            confirm_link=url_for(
                'auth.update_password_confirm',
                token=current_user.generate_confirmation_token({'psw': generate_password_hash(data['password'])}),
                _external=True
            )
        )
    except SMTPDataError:
        # 发送邮件失败，表明邮箱是无效的
        return {'status': 0, 'message': '发送邮件失败，请检查邮箱是否仍然可用'}
    return {'status': 1, 'message': '确认邮件已发送至邮箱，请前往确认'}


@auth.route('/forget_password')
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('auth.update_password'))
    return render_template('auth/forget-password.html')


@auth.route('/send_confirm/forget_password', methods=['POST'])
def send_confirm_forget_password():
    # 检查是否是已登录状态，若是则不允许做任何操作
    if current_user.is_authenticated:
        return {'message': '请先登出'}

    data = request.json

    # 表单验证
    cus = Customer.query.filter_by(customer_email=data['email']).first()
    if cus is None:
        return {'status': 0, 'message': '该邮箱未注册'}
    elif not cus.confirmed:
        return {'status': 0, 'message': '您已注册但邮箱未确认，请重新注册！'}
    elif cus.verify_password(data['password']):
        return {'status': 0, 'message': '新密码不能与旧密码一样！'}

    # 发送确认邮件
    try:
        send_email(
            cus.customer_email,
            '忘记密码',
            'auth/update_password_confirm',
            customer_name=cus.customer_name,
            confirm_link=url_for(
                'auth.update_password_confirm',
                token=cus.generate_confirmation_token({'psw': generate_password_hash(data['password'])}),
                _external=True
            )
        )
    except SMTPDataError:
        # 发送邮件失败，表明邮箱是无效的
        return {'status': 0, 'message': '发送邮件失败，请检查邮箱是否仍然可用'}
    return {'status': 1, 'message': '发送邮件成功，请前往邮箱确认'}


@auth.route('/update_email')
@login_required
def update_email():
    return render_template('auth/update-email.html')


@auth.route('/send_confirm/update_email', methods=['POST'])
@login_required
def send_confirm_update_email():
    email = request.json['email']

    # 检查邮箱是否存在
    if Customer.query.filter_by(customer_email=email).first() is not None:
        return {'status': 0, 'message': '该邮箱已被注册'}
    try:
        send_email(
            email,
            '更改邮箱',
            'auth/update_email_confirm',
            customer_name=current_user.customer_name,
            confirm_link=url_for(
                'auth.update_email_confirm',
                token=current_user.generate_confirmation_token({'em': email}),
                _external=True
            )
        )
    except SMTPDataError:
        # 发送邮件失败，表明邮箱是无效的
        return {'status': 0, 'message': '发送邮件失败，请检查邮箱是否仍然可用'}
    return {'status': 1, 'message': '发送邮件成功，请前往邮箱确认'}


@auth.route('/update_email_confirm')
def update_email_confirm():
    result = check_token(request.args.get('token'))
    if not result['status']:
        return result['response']
    data = result['data']
    cus = result['cus']
    cus.update_customer_email(data['em'])
    db.session.add(cus)
    db.session.commit()
    return render_template('auth/confirm.html', info='验证成功', info_type='hint')
