from time import time as get_timestamp
from authlib.jose import jwt
from flask import render_template
from config import Config
from ..models import Customer


def check_token(token) -> dict:
    if not isinstance(token, str):
        return {'status': 0, 'response': render_template('auth/confirm.html')}
    try:
        data = jwt.decode(token, Config.SECRET_KEY)
    except Exception:
        return {'status': 0, 'response': render_template('auth/confirm.html', info='验证失败，无效链接', info_type='error')}
    if data['now'] + Config.TOKEN_EFFECTIVE_TIME < get_timestamp():
        return {'status': 0, 'response': render_template('auth/confirm.html', info='验证失败，链接已过期', info_type='error')}
    cus = Customer.query.filter_by(customer_id=data['customer_id']).first()
    if cus is None:
        return {'status': 0, 'response': render_template('auth/confirm.html', info='验证失败，无效链接', info_type='error')}
    return {'status': 1, 'data': data, 'cus': cus}
